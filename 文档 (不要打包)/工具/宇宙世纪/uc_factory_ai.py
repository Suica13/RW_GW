# Executed after branch pruning. Preserve normal/specialist priorities and fill idle choices.
# Native UnitTemplate conditions still enforce unlocks, unit caps, costs and an empty queue.
AI_FALLBACK_FACTORIES = {}
for name, records in ENT.items():
    record = choose(name)
    if not record or record['era'] not in ['0079','0087']:
        continue
    if not record['path'].startswith('Units/Buildings/Factory/Faction/'):
        continue
    key = (record['era'], record['path'])
    text = DB[key]
    sections = local(text)
    receiver = sections.get('hiddenAction_Get_AutoProduce', {})
    if not receiver:
        continue
    candidates = []
    # Later-era ordinary units first; older base units remain a last resort.
    normal_groups = sorted((s for s in sections if s.startswith('hiddenAction_AutoProduce_') and s.endswith('_NormalUnits')), reverse=True)
    for section in normal_groups:
        for action in sections[section].get('alsoTriggerAction','').split(','):
            action = action.strip()
            if action.startswith('AutoProduce_') and action not in candidates and not BAD_ACTION_RE.search(action):
                candidates.append(action)
    if not candidates:
        continue
    fallback_calls = []
    for index, original in enumerate(candidates):
        fallback = 'UC_AutoProduceFallback_' + str(index)
        fallback_calls.append(fallback)
        text += f'\n[hiddenAction_{fallback}]\n@copyFromSection:hiddenAction_{original}\n@define AutoProduceIndexMin=0\n@define AutoProduceIndexMax=1000\n'
    text += '\n[hiddenAction_UC_TryAutoProduceFallback]\nrequireConditional:if self.queueSize()<=0\nalsoTriggerAction:' + ','.join(fallback_calls) + '\n'
    existing = receiver.get('alsoTriggerAction','').strip()
    text = edit(text,'hiddenAction_Get_AutoProduce','alsoTriggerAction',existing+',UC_TryAutoProduceFallback')
    DB[key] = text
    AI_FALLBACK_FACTORIES[name] = candidates
(OUT/'ai-production-fallbacks.json').write_text(json.dumps(AI_FALLBACK_FACTORIES,ensure_ascii=False,indent=2),encoding='utf-8')
