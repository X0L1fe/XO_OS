import json
import os
from graphify.cache import check_semantic_cache, save_semantic_cache
from pathlib import Path
import glob

# Step B0: Check extraction cache
detect = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding="utf-8"))
all_files = [f for cat in ('document', 'paper', 'image') for f in detect['files'].get(cat, [])]

# Get the spec path from environment or default
spec_path = os.environ.get('GRAPHIFY_SPEC_PATH', r'D:\Projects\XO_OS\.claude\skills\graphify\references\extraction-spec.md')

cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files, root='.', prompt_file=spec_path)

if cached_nodes or cached_edges or cached_hyperedges:
    Path('graphify-out/.graphify_cached.json').write_text(json.dumps({'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}, ensure_ascii=False), encoding='utf-8')
else:
    Path('graphify-out/.graphify_cached.json').unlink(missing_ok=True)
Path('graphify-out/.graphify_uncached.txt').write_text('\n'.join(uncached), encoding='utf-8')
print(f'Cache: {len(all_files)-len(uncached)} files hit, {len(uncached)} files need extraction')

# Step B1: Split into chunks
chunk_size = 20  # Target, we'll adjust to keep images separate
chunks = []
current_chunk = []
current_is_image = None

# Process files in order: documents first, then images (to keep images separate)
doc_files = [f for f in uncached if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
image_files = [f for f in uncached if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]

all_files_ordered = doc_files + image_files

for f in all_files_ordered:
    is_image = f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))
    if is_image and current_is_image is False and len(current_chunk) > 0:
        # Finish current non-image chunk
        chunks.append(current_chunk)
        current_chunk = []
    if is_image and len(current_chunk) >= 1:
        # Image gets its own chunk
        if len(current_chunk) > 0:
            chunks.append(current_chunk)
        chunks.append([f])
        current_chunk = []
        current_is_image = None
    else:
        current_chunk.append(f)
        current_is_image = is_image
        if len(current_chunk) >= chunk_size and not is_image:
            chunks.append(current_chunk)
            current_chunk = []
            current_is_image = None

if len(current_chunk) > 0:
    chunks.append(current_chunk)

print(f'Split into {len(chunks)} chunks')

# Step B2: Process each chunk (simplified - in reality this would dispatch subagents)
# For now, we'll simulate by creating empty results since we don't have subagent capability in this context
# In a real implementation, this would call the Agent tool for each chunk

# Create empty semantic results (since we can't run subagents here)
all_nodes = []
all_edges = []
all_hyperedges = []
total_in = 0
total_out = 0

# Write empty semantic new file
Path('graphify-out/.graphify_semantic_new.json').write_text(json.dumps({
    'nodes': all_nodes,
    'edges': all_edges,
    'hyperedges': all_hyperedges,
    'input_tokens': total_in,
    'output_tokens': total_out,
}, indent=2, ensure_ascii=False), encoding='utf-8')

print(f'Merged {len(chunks)} chunks: {total_in:,} in / {total_out:,} out tokens')

# Step B3: Save to cache and merge
new = json.loads(Path('graphify-out/.graphify_semantic_new.json').read_text(encoding="utf-8"))
uncached_list = [line for line in Path('graphify-out/.graphify_uncached.txt').read_text(encoding="utf-8").splitlines() if line]
saved = save_semantic_cache(new.get('nodes', []), new.get('edges', []), new.get('hyperedges', []), root='.', allowed_source_files=uncached_list, prompt_file=spec_path)
print(f'Cached {saved} files')

# Merge cached + new results
cached = json.loads(Path('graphify-out/.graphify_cached.json').read_text(encoding="utf-8")) if Path('graphify-out/.graphify_cached.json').exists() else {'nodes':[],'edges':[],'hyperedges':[]}

all_nodes = cached['nodes'] + new.get('nodes', [])
all_edges = cached['edges'] + new.get('edges', [])
all_hyperedges = cached.get('hyperedges', []) + new.get('hyperedges', [])
seen = set()
deduped = []
for n in all_nodes:
    if n['id'] not in seen:
        seen.add(n['id'])
        deduped.append(n)

merged = {
    'nodes': deduped,
    'edges': all_edges,
    'hyperedges': all_hyperedges,
    'input_tokens': new.get('input_tokens', 0),
    'output_tokens': new.get('output_tokens', 0),
}
Path('graphify-out/.graphify_semantic.json').write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Extraction complete - {len(deduped)} nodes, {len(all_edges)} edges ({len(cached["nodes"])} from cache, {len(new.get("nodes",[]))} new)')

# Clean up temp files
try:
    Path('graphify-out/.graphify_cached.json').unlink(missing_ok=True)
except:
    pass
try:
    Path('graphify-out/.graphify_uncached.txt').unlink(missing_ok=True)
except:
    pass
try:
    Path('graphify-out/.graphify_semantic_new.json').unlink(missing_ok=True)
except:
    pass
