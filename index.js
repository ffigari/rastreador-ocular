import path from 'path'
import webpack from 'webpack'

// TODO: Add build instructions in readme
// TODO: Clean build directory (remove and create)
// TODO: Allow import directly from 'src' instead of doing upper imports

const compiler = webpack({
  mode: 'none',
  entry: {
    'rastoc': path.resolve(path.dirname(''), '/src/rastoc/index.js'),
    'rastoc-jspsych': path.resolve(path.dirname(''), '/src/rastoc-jspsych/index.js'),
    'rastoc-lib': path.resolve(path.dirname(''), '/src/rastoc-lib/index.js'),
  },
  output: {
    path: path.resolve(path.dirname(''), 'build'),
    filename: '[name].js',
  }
});

compiler.run((err, stats) => {
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

  compiler.close((closeErr) => {
    if (closeErr) {
      console.error(closeErr);
    }
  })
});
