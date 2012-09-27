/* 
 * A name server which sends back the IP address of its client, the
 * recursive resolver. When queried for type TXT, it sends back the text
 * form of the address.  When queried for type A (resp. AAAA), it sends
 * back the IPv4 (resp. v6) address.
 *
 * Similar services: whoami.ultradns.net, whoami.akamai.net. Also (but it
 * is not their normal goal): rs.dns-oarc.net, porttest.dns-oarc.net,
 * amiopen.openresolvers.org.
 *
 * Original version from:
 * Stephane Bortzmeyer <stephane+grong@bortzmeyer.org>
 *
 * Adapted to Go DNS (i.e. completely rewritten)
 * Miek Gieben <miek@miek.nl>
 */

package main

import (
	"flag"
	"fmt"
	"github.com/miekg/dns"
	"log"
	"os"
	"os/signal"
	"runtime/pprof"
	"strings"
	"syscall"
	"github.com/chuangbo/jianbing-dictionary-dns/golang/jianbing-dns/stardict"
)

var (
	printf   *bool
	compress *bool
)

const ttl = 5

func handleReflect(w dns.ResponseWriter, r *dns.Msg) {
	// TC must be done here
	m := new(dns.Msg)
	m.SetReply(r)
	m.Compress = *compress

	t := new(dns.RR_TXT)
	t.Hdr = dns.RR_Header{Name: r.Question[0].Name, Rrtype: dns.TypeTXT, Class: dns.ClassINET, Ttl: ttl}

	word := r.Question[0].Name
	word = word[:strings.Index(word, ".")]
	// fmt.Println(word)
	t.Txt = []string{stardict.Check(word)}

	m.Answer = append(m.Answer, t)

	if *printf {
		fmt.Printf("%v\n", m.String())
	}
	w.Write(m)
}

func serve(net string) {
	err := dns.ListenAndServe(":53", net, nil)
	if err != nil {
		fmt.Printf("Failed to setup the "+net+" server: %s\n", err.Error())
	}
}

func main() {
	cpuprofile := flag.String("cpuprofile", "", "write cpu profile to file")
	printf = flag.Bool("print", false, "print replies")
	compress = flag.Bool("compress", false, "compress replies")
	flag.Usage = func() {
		flag.PrintDefaults()
	}
	flag.Parse()
	if *cpuprofile != "" {
		f, err := os.Create(*cpuprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	stardict.PrepareIndex()

	dns.HandleFunc(".", handleReflect)
	go serve("tcp")
	go serve("udp")

	fmt.Println("Already here")
	sig := make(chan os.Signal)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)

	forever:
	for {
		select {
		case s := <- sig:
			fmt.Printf("Signal (%d) received, stopping\n", s)
			break forever
		}
	}
}
