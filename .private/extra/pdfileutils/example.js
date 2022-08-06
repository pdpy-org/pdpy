var pdfu = require('pd-fileutils')
  , fs = require('fs')
  , patchStr, patch

// Read the file
patchStr = fs.readFileSync('../pd2wap/hello_world/hello_world.pd').toString()
// console.log(patchStr)
// Parse the read file
patch = pdfu.parse(patchStr)
fs.writeFileSync("./example.json",JSON.stringify(patch))
// console.log(patch)
svgstuff = pdfu.renderSvg(patch)
fs.writeFileSync("./example.svg",svgstuff)