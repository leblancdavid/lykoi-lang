// Reproduce list-result validation in an already installed SDK, no dependency install.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const sdk = path.join(process.env.APPDATA, 'npm/node_modules/@optave/codegraph/node_modules/@modelcontextprotocol/sdk');
const { ListToolsResultSchema } = await import(pathToFileURL(path.join(sdk, 'dist/esm/types.js')));
const packageInfo = JSON.parse(fs.readFileSync(path.join(sdk, 'package.json'), 'utf8'));
const results = {};
for (const label of ['SCHEMA-root_union', 'SCHEMA-typed_root_union', 'ORIGINAL', 'ANNOTATED']) {
  const lines = fs.readFileSync(new URL(`./${label}/MCP.jsonl`, import.meta.url), 'utf8').trim().split('\n').map(JSON.parse);
  const listed = lines.find(x => x.request.method === 'tools/list').response.result;
  const parsed = ListToolsResultSchema.safeParse(listed);
  results[label] = {accepted: parsed.success, exception: parsed.success ? null : parsed.error.name,
                    issues: parsed.success ? [] : parsed.error.issues};
}
console.log(JSON.stringify({sdk_version: packageInfo.version, installed_sdk_path: sdk, results,
  limitation: 'Separate installed SDK reproduction, not interception of OpenCode bundled exception. Matching-version public OpenCode source pins SDK1.29.0.'}, null, 2));
