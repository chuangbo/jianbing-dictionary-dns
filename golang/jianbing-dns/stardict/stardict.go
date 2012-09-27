package stardict

import (
    "fmt"
    "runtime"
    "path"
    "os"
    "io/ioutil"
    "encoding/binary"
    "bytes"
    "strings"
)

var _, filename, _, _ = runtime.Caller(0)
var base = path.Join(path.Dir(filename), "../../../stardict-lazyworm-ec-2.4.2/lazyworm-ec")

var word_idx = make(map[string]string)

func PrepareIndex() {
    idx_data, err := ioutil.ReadFile(base + ".idx")
    if err != nil {
        fmt.Printf("Failed to open the dictionary: %s\n", err.Error())
    }

    dict_data, err := os.Open(base + ".dict")
    if err != nil {
        fmt.Printf("Failed to open the dictionary: %s\n", err.Error())
    }

    reader := bytes.NewBuffer(idx_data)

    for {
        word, err := reader.ReadString('\x00')
        word = strings.TrimRight(word, "\x00")

        if err != nil {
            break
        }

        // offset
        var offset int32
        b_offset := make([]byte, 4)
        if n, err := reader.Read(b_offset); err != nil || n != 4 {
            fmt.Println("offset err", word, n, err)
            break
        }
        binary.Read(bytes.NewBuffer(b_offset), binary.BigEndian, &offset)


        // length
        var length int32
        b_length := make([]byte, 4)
        if n, err := reader.Read(b_length); err != nil || n != 4 {
            fmt.Println("length err", word, n, err)
            break
        }
        binary.Read(bytes.NewBuffer(b_length), binary.BigEndian, &length)


        // desc
        desc := make([]byte, length)
        dict_data.ReadAt(desc, int64(offset))

        word_idx[word] = string(desc)


        // fmt.Println(word, string(desc))
        
    }

}


func Check(word string) string {
    desc, exists := word_idx[word]
    if !exists {
        return "no such word " + word
    }
    return desc
}
