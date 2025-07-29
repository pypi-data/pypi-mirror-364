# BrainCo Proto Message SDK

<!-- [View documentation for this example online][dox] or
[View compiled example online][compiled]

[dox]: https://rustwasm.github.io/docs/wasm-bindgen/examples/add.html
[compiled]: https://rustwasm.github.io/wasm-bindgen/exbuild/add/ -->

You can build the example locally with:

```shell
yarn serve
```

and then visiting http://localhost:8080 in a browser should run the example!

sample code in `example_edu.js`

```js
import { MessageParser, MsgType } from "./pkg";

// Initialize the message parser
const parserEdu = new MessageParser(MsgType.Edu);
// const parserMorpheus = new MessageParser(MsgType.Morpheus);

// Function to handle incoming data
function processEduData(data) {
  const uint8Array = new Uint8Array(data);
  parserEdu.receive_data(uint8Array);
}

// Function to continuously fetch and log messages
async function listenEduMessages() {
  while (true) {
    try {
      // Fetch the next message
      const msg = await parserEdu.next_message();
      console.log("Received EDU message:", msg);
    } catch (error) {
      // Handle any errors that occur during message fetching
      console.error("Error while fetching message:", error);
    }
    // Optional: consider add a delay to prevent the loop from consuming too much CPU
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
}

// Start listening for messages
listenEduMessages();

processEduData([66, 82, 78, 67, 2, 12, 1, 2, 0, 1, 2, 0, 8, 1, 112, 130]);
processEduData([66, 82, 78, 67, 2, 12, 1, 3, 0, 1, 2, 0, 8, 154, 5, 233, 27]);
```

then ouput will be

```log
// edu.log
index.js:29 Received EDU message: {"EduMessage":{"App2Dongle":{"msgId":1}}}
index.js:29 Received EDU message: {"EduMessage":{"App2Dongle":{"msgId":666}}}
```

```log
// morp.log
index.js:44 Received Morpheus message: {"Morpheus":{"Bt2App":{"msgId":1}}}
index.js:44 Received Morpheus message: {"Morpheus":{"Mcu2App":{"msgId":11,"otaCfgResp":{"state":"REBOOTED"}}}}
```
