import time
import ffmpeg
from billiard.pool import Pool
from webplayer.celery import celery_app


def get_chapters(file_name):
    try:
        probe = ffmpeg.probe(file_name, show_chapters=None)

        return [{'title': chapter['tags']['title'], 'start_time': int(float(chapter['start_time']))}
            for chapter in probe['chapters']]
    except ffmpeg._run.Error as err:
        print(err)
        return []


def enrich_file_entry(entry):
    target = entry['path'] if 'path' in entry else entry['url']
    if 'chapters' not in entry:
        entry['chapters'] = get_chapters(target)
    return entry


def reset_chapter_info(list_entry):
    for file_entry in list_entry.files:
        if 'chapters' in file_entry:
            file_entry.pop('chapters')


def enrich_with_chapters(repo, force=False):
    start = time.time_ns()
    all_lists = repo.list()
    with Pool(50) as pool:
        for lst in all_lists:
            entry = repo.get(lst.id)
            if force:
                reset_chapter_info(entry)
            new_files = pool.map(enrich_file_entry, entry.files)

            enriched_list = entry._replace(files=new_files)
            repo.put(enriched_list)
    end = time.time_ns()
    print(f'metadata update took {(end-start)/1000000000} seconds')


@celery_app.task
def async_enrichment(repo_type, db_file_path, force=False):
    from webplayer.file_handler import DirectoryRepo
    from webplayer.list_handler import ListRepo

    repo_map = {
        'list': ListRepo,
        'file': DirectoryRepo
    }

    RepoType = repo_map.get(repo_type)
    if RepoType:
        repo = RepoType(db_file_path)
        enrich_with_chapters(repo, force)
    else:
        print('no repository could be created')
