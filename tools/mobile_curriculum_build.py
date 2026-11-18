#!/usr/bin/env python3
"""Compile authored conceptual lessons and the frozen Python contract tutorials.

Run from any directory. No network dependency; no repeated generated lesson text.
The seed contains only stable IDs/chapter/topic metadata, never old lesson prose.
"""
from copy import deepcopy
import json
from pathlib import Path

from mobile_curriculum_content import LESSONS
from mobile_curriculum_glossary import prerequisites
from mobile_curriculum_code_checks import QUESTIONS as EARLY
from mobile_curriculum_code_checks_late import QUESTIONS as LATE
from mobile_curriculum_supplements import SUPPLEMENTS, MOVES, DEMONSTRATIONS, SOURCE_LINKS

ROOT = Path(__file__).resolve().parents[1]
CAST = ['Ирис','Эйла','Мира','Селена']

def question(row, rotation):
    prompt, right, wrong1, wrong2, feedback = row
    options = [right, wrong1, wrong2]
    options = options[rotation:] + options[:rotation]
    return dict(question=prompt, options=options, answer=options.index(right), explanation=feedback)

def build():
    seed = json.loads((ROOT/'tools/mobile_curriculum_seed.json').read_text())
    exercises = json.loads((ROOT/'web/python/exercises.json').read_text())['exercises']
    by_code = {e['id']: e for e in exercises}
    questions = EARLY | LATE
    assert set(questions) == set(by_code)
    levels = deepcopy(seed['levels'])
    by_number = {l['number']: l for l in levels}
    original_topics = {t['name'] for l in levels for t in l['topics']}
    for before, after, names in MOVES:
        moving = [t for t in by_number[before]['topics'] if t['name'] in names]
        assert {t['name'] for t in moving} == set(names), (before, after, names)
        by_number[before]['topics'] = [t for t in by_number[before]['topics'] if t['name'] not in names]
        by_number[after]['topics'].extend(moving)
    for level in levels:
        n = level['number']
        npc = CAST[((n-1)//3) % len(CAST)]
        if level['pythonId']:
            exercise = by_code[level['pythonId']]
            assert exercise['levelId'] == level['id']
            teaching = deepcopy(exercise['teaching'])
            title = exercise['title']
            scene = exercise['purpose']
            check, transfer = (questions[exercise['id']][kind] for kind in ('check','transfer'))
            practice_kind = 'python'
            sources = exercise['sources']
            level['exerciseContract'] = exercise['brief']
        else:
            authored = LESSONS[n]
            title, scene = authored['title'], authored['scene']
            check, transfer = authored['check'], authored['transfer']
            practice_kind = 'concept'
            sources = [authored['source']]
            teaching = dict(
                goal=authored['goal'], prerequisites=prerequisites(authored['prerequisites']),
                steps=[dict(title=t,text=body) for t,body in authored['steps']],
                workedExample=dict(title='Разбор на другом случае',steps=authored['worked']),
                taskBridge='Разберите предложенный случай по тому же правилу. Укажите, какие данные изменились и почему это меняет решение. Все необходимые определения и метод приведены выше; внешние ссылки нужны только для углубления.',
                pitfalls=[dict(symptom=authored['pitfall'][0],explanation=authored['pitfall'][1])],
                interview=check[0]+' Объясните механизм и границу применимости, затем приведите свой небольшой пример.'
            )
        teaching['steps'].extend(dict(title=t,text=body) for t,body in SUPPLEMENTS.get(n,[]))
        if n in DEMONSTRATIONS:
            teaching['demonstration'] = DEMONSTRATIONS[n]
        level.update(
            title=title, npc=npc, objective=teaching['goal'], teaching=teaching,
            lesson=[step['title']+'\n'+step['text'] for step in teaching['steps']],
            workedExample='\n'.join(teaching['workedExample']['steps']),
            practiceKind=practice_kind, mandatoryCombat=False, learningVersion=2,
            story=[dict(speaker=npc,text=scene),dict(speaker='Вы',text='Разберём механизм на небольшом примере, затем проверим его в новой ситуации.')],
            check=question(check,n%3), transfer=question(transfer,(n+1)%3),
            hint=teaching['pitfalls'][0]['explanation'],
            remedial='Вернитесь к разобранному примеру: '+teaching['workedExample']['steps'][0],
            sources=list(dict.fromkeys(sources+[t['source'] for t in level['topics']]+SOURCE_LINKS.get(n,[]))),
            reflection=dict(prompt=teaching['interview'],model=check[4]+' '+transfer[4],
                checklist=['Названо правило, определение или инвариант этого эпизода.','Показано его применение к конкретным данным.','Указан случай, когда результат или допустимое действие меняется.']),
            reward=dict(id=f'r{n:03}',text='Вы обсудили результат и его ограничения. Следующая встреча продолжит эту работу.'),
            minutes=35 if practice_kind=='python' else 18,
        )
        # No combat appears in the new default route. Keep legacy generator
        # metadata for old optional sandbox code, labelled explicitly.
        level['battle']['legacyOnly'] = True
        level['battle']['goal'] = 'Не входит в прохождение V2.'
        for topic in level['topics']:
            topic['lessonId'] = level['id']
            # A prose explanation is not evidence of executable mastery.
            topic['depth'] = 'apply' if practice_kind=='python' else 'explain'
            topic['example'] = topic['example'].replace('Каэль','Селена').replace('Каэля','Селены')
    assert len(levels)==100 and sum(bool(l['pythonId']) for l in levels)==40
    assert {t['name'] for l in levels for t in l['topics']} == original_topics
    chapters=seed['chapters']
    for chapter in chapters:
        chapter['intro']=chapter['intro'].replace('Новый спутник Ирис ещё не знает','Команда Ирис выясняет').replace('какие следы','какие записи')
    campaign=dict(version=2,teachingVersion=2,
        title='asterion. elf beauties teach me all about Machine Learning. V2',
        pedagogy='definition → worked example → contract-aligned practice → explained transfer → reflection',
        chapters=chapters,levels=levels)
    destination=ROOT/'web/data/campaign.json'
    destination.write_text(json.dumps(campaign,ensure_ascii=False,indent=2)+'\n')
    print(f'Published {len(levels)} lessons, {len(exercises)} Python contracts, {len(original_topics)} distinct inventory labels; {destination.stat().st_size} bytes')

if __name__=='__main__':
    build()
