import fs from 'fs'
import path from 'path'
import webpack from 'webpack'

const buildDir = 'www/build'
fs.rmdirSync(buildDir, { recursive: true });

const compiler = webpack({
  mode: 'none',
  entry: {
    'rastoc': path.resolve(path.dirname(''), '/src/rastoc/index.js'),
    'rastoc-jspsych': path.resolve(path.dirname(''), '/src/rastoc-jspsych/index.js'),
  },
  output: {
    path: path.resolve(path.dirname(''), buildDir),
    filename: '[name].js',
  }
});

// TODO: Distinguish build and watch
//       Building has to be done by doing
//         'compiler.run((err, stats) => {
//
//            ...
//
//            compiler.close((closeErr) => {
//              if (closeErr) {
//                console.error(closeErr);
//              }
//            })
//         })'
compiler.watch({}, (err, stats) => {
  if (err) {
    console.error(err.stack || err);
    if (err.details) {
      console.error(err.details);
    }
    return;
  }

  const info = stats.toJson();

  if (stats.hasErrors()) {
    info.errors.forEach(err => console.error(err));
    return;
  }

  if (stats.hasWarnings()) {
    info.warnings.forEach(message => console.log(message));
  }

  console.log(`[${(new Date).toISOString()}] compiled`);
});
