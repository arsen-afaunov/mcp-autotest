import * as esbuild from 'esbuild';
import fs from 'fs';
import path from 'path';
import { config as dotenvConfig } from 'dotenv';

const WATCH = process.argv.includes('-w') || process.argv.includes('--watch');

dotenvConfig({ path: path.resolve('..', '.env') });

const SRC_DIR = 'src';
const OUT_DIR = 'dist';

const ENTRY_POINTS = [
  path.join(SRC_DIR, 'service_worker.ts'),
  path.join(SRC_DIR, 'offscreen.ts'),
];

const STATIC_FILES = [
  path.join(SRC_DIR, 'manifest.json'),
  path.join(SRC_DIR, 'offscreen.html'),
];

function copyStaticFiles(): void {
  for (const file of STATIC_FILES) {
    const dest = path.join(OUT_DIR, path.basename(file));
    fs.copyFileSync(file, dest);
    console.log(`[copy] ${file} → ${dest}`);
  }
}

async function build(): Promise<void> {
  const options: esbuild.BuildOptions = {
    entryPoints: ENTRY_POINTS,
    outdir: OUT_DIR,
    bundle: true,
    format: 'esm',
    target: 'chrome120',
    sourcemap: true,
    define: {
      '__BUILD_WS_HOST__': JSON.stringify(process.env.WS_HOST || 'localhost'),
      '__BUILD_WS_PORT__': JSON.stringify(process.env.WS_PORT || '8765'),
    },
  };

  if (WATCH) {
    const ctx = await esbuild.context(options);
    await ctx.watch();
    console.log('[watch] Build started, watching for changes...');
  } else {
    await esbuild.build(options);
    console.log('[build] Done');
  }

  copyStaticFiles();
}

build().catch((err: unknown) => {
  console.error(err);
  process.exit(1);
});
