# Executed after the ordinary branch-pruning pass.
# Keep source-era factory priorities, random ranges, caps, prices and HQ scheduling.
# UC deliberately does not broadcast to every factory or bypass native random choices.
AI_FALLBACK_FACTORIES = {}
(OUT/'ai-production-fallbacks.json').write_text(json.dumps(AI_FALLBACK_FACTORIES,indent=2),encoding='utf-8')
