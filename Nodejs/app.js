
const ScrapeProxy = require("./proxy.js")
const iconv = require('iconv-lite');
const cheerio = require('cheerio');
const request = require('request-promise');

const sp = new ScrapeProxy();

async function task(i) {

  let j = request.jar()
  let result = [];

  const tempHead = sp.getRandomUserAgent();
  const content = await request.get({
    headers: tempHead,
    uri: `${i}`,
    jar: j,
    encoding: null,
    }).then(d => {
      let str = iconv.decode(d, "UTF-8");
      const $ = cheerio.load(str);
      return $('#data').text();
  });

  result.push({
    content: content,
  });
  return result;
}

// async function writeDatabase(records) {
//   // write DB or File here.
// }

async function main() {
  const start = Date.now();
  
  const promises = [1, 2, 3].map( i => {
    return new Promise((resolve, reject) => {
      try {
        task(i).then(d => resolve(d));
      } catch (error) {
        return reject(error);
      }
    });
  });

  const records = await Promise.all(promises);

  let end =  Date.now();
  console.log((end - start)/1000);

  // await writeDatabase(records);

  end =  Date.now();
  console.log((end - start)/1000);
}

main();
