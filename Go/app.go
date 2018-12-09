package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strconv"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"golang.org/x/text/encoding/traditionalchinese"
	"golang.org/x/text/transform"
)

var jar, _ = cookiejar.New(nil)
var client = http.Client{
	Jar: jar,
}
var userAgentList = []string{}

type article struct {
	title   string
	content string
}

func task(i string, linkChan chan article) {
	fmt.Println(i)
	url := "https://example.com/example/" + i

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatalln(err)
		panic(err)
	}

	ua := userAgentList[rand.Intn(len(userAgentList))]
	req.Header.Set("User-Agent", ua)

	resp, err := client.Do(req)
	if err != nil {
		log.Fatalln(err)
		panic(err)
	}
	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatalln(err)
		panic(err)
	}
	resp.Body.Close()
	outByte, err := decode(data)
	if err != nil {
		log.Fatal(err)
		panic(err)
	}
	output := string(outByte)
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(string(output)))
	if err != nil {
		log.Fatal(err)
		panic(err)
	}

	doc.Find(`div`).Each(func(j int, selection *goquery.Selection) {
		href, _ := selection.Attr("href")
		title := selection.Text()
		linkChan <- article{title, href}
	})
	close(linkChan)
}

func decode(s []byte) ([]byte, error) {
	I := bytes.NewReader(s)
	O := transform.NewReader(I, traditionalchinese.Big5.NewDecoder())
	d, e := ioutil.ReadAll(O)
	if e != nil {
		return nil, e
	}
	return d, nil
}

func init() {
	b, err := ioutil.ReadFile("ChromeUserAgent.txt")
	if err != nil {
		log.Fatalln(err)
		return
	}
	str := string(b)
	userAgentList = strings.Split(str, "\n")
}

func main() {

	_, err := client.PostForm("https://www.example.com", url.Values{"1": {"1"}})
	if err != nil {
		log.Fatalln(err)
		return
	}

	const pageNum = 100
	linkChan := [pageNum]chan article{}

	for i := 1; i <= pageNum; i++ {
		linkChan[i-1] = make(chan article, 20)
		go task(strconv.Itoa(i), linkChan[i-1])
	}
}
