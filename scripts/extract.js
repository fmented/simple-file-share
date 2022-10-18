const fs = require('fs');
const path = require('path')

const directoryPath = path.join(__dirname, '..', 'icons');

function extract(file) {
    var body = fs.readFileSync(path.join(directoryPath, file));
    return `export const __${file.replace('.svg', '')} = \`${body.toString('utf8')}\``
}

fs.readdir(directoryPath, function (err, files) {
    if (err) return console.log('Unable to scan directory: ' + err);  
    data = ''
    files.forEach(function (file) {
        data += `\n${extract(file)}`
    });

    fs.writeFileSync(path.join(__dirname, '..' ,  'src', 'iconlist.js'), data)
});