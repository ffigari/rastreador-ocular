import fs from 'fs'
import path from 'path'
import webpack from 'webpack'

const usage = () => {
  console.log(
  `index.js - compile relevant browser javascript files
  - 'node index.js build': build once
  - 'node index.js watch': start on watch mode to recompile on each change`
  );
  process.exit(1);
}
if (process.argv.length < 3) {
  usage();
}
const action = process.argv[2];

fs.rmSync('www/build', { recursive: true, force: true });
const compiler = webpack({
  mode: 'none',
  entry: {
    'build/eye-tracker': path.resolve(
      path.dirname(''), '/eye-tracker/index.js'),
    'build/jspsych-interface': path.resolve(
      path.dirname(''), '/jspsych-interface/index.js'),
  },
  output: {
    path: path.resolve(path.dirname(''), 'www'),
    filename: '[name].js',
  }
});

const getCompilationHandler = (compiler) => {
  const closeCompiler = !!compiler;
  return (err, stats) => {
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
      return;
    }

    console.log(`[${(new Date).toISOString()}] compiled`);

    if (closeCompiler) {
      compiler.close((closeErr) => {
        if (closeErr) {
          console.error(closeErr);
        }
      })
    }
  }
};

if (action === 'watch') {
  compiler.watch({}, getCompilationHandler());
} else if (action === 'build') {
  compiler.run(getCompilationHandler(compiler));
} else {
  usage();
}
