'use strict';

const os = require('os');
const path = require('path');
const harness = require('./harness');

function stmtCount(body) {
  const m = /-- (\d+) statements recorded/.exec(body);
  return m ? parseInt(m[1], 10) : 0;
}

function takeLine(body, name) {
  const re = new RegExp(`${harness.mark(name + ' ')}([^\\n]*)\\n`);
  const m = re.exec(body);
  if (!m) return [null, body];
  return [m[1], body.slice(0, m.index) + body.slice(m.index + m[0].length)];
}

function takeStrings(body) {
  const marker = harness.mark('ENVLOG-STRINGS\n');
  const idx = body.indexOf(marker);
  if (idx !== -1) {
    return [body.slice(0, idx), body.slice(idx + marker.length)];
  }
  return [body, null];
}

function header(inputPath, notes = []) {
  let h = '';
  for (const n of notes) h += `-- ${n}\n`;
  return h;
}

function statusLine(body) {
  // First line is "-- run status: ..."; a script error carries its Luau
  // traceback on the following "--   ..." lines. Print them (bounded) so the
  // failing VM frame is visible in the log, not just the error message.
  const lines = (body || '').split('\n');
  const first = lines[0] || '';
  process.stderr.write('[*] ' + first.replace(/^--\s*/, '') + '\n');
  let n = 0;
  for (let i = 1; i < lines.length && n < 30; i++) {
    if (!/^--   /.test(lines[i])) break;
    process.stderr.write('[*]   ' + lines[i].replace(/^--   /, '').slice(0, 300) + '\n');
    n++;
  }
}

module.exports = { stmtCount, takeLine, takeStrings, header, statusLine };
