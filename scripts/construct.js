const fs = require('fs')
const path = require('path')

const js = fs.readFileSync(path.join(...[__dirname, ...'../public/build/bundle.js'.split('/')]))

const globalCss = fs.readFileSync(path.join(...[__dirname, ...'../public/global.css'.split('/')]))
const css = fs.readFileSync(path.join(...[__dirname, ...'../public/build/bundle.css'.split('/')]))

const mime = fs.readFileSync(path.join(...[__dirname, ...'../extras/mime.json'.split('/')]))

const template = fs.readFileSync(path.join(...[__dirname, ...'../extras/template.py'.split('/')]))

const favicon = fs.readFileSync(path.join(...[__dirname, ...'../icons/favicon.svg'.split('/')]))

function preprocessJS(str) {
    return String(str).replace(/\\n/g, '').replace(/\n/g, '')
}

function preprocessCSS(str) {
    return String(str).replace(/(\n|\t)/g, '')
}

function preprocessJSON(str) {
    return preprocessCSS(str)
}

function build(template, js, css, json, favicon) {
    const CSS = preprocessCSS(css)
    const JS = preprocessJS(js)
    const _JSON = preprocessJSON(json)

    return String(template)
            .replace(/\$\$JS/g, JS)
            .replace(/\$\$CSS/g, CSS)
            .replace(/\$\$MIME/g, _JSON)
            .replace(/\$\$FAVICON/g, favicon)
}

const data = build(template, js, `${globalCss} ${css}`, mime, favicon)

fs.writeFileSync(path.join(__dirname, '..' , 'server.py'), data)