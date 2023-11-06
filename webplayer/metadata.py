import time
from multiprocessing import Pool, Process
import ffmpeg


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


def enrich_with_chapters(repo):
    start = time.time_ns()
    all_lists = repo.list()
    for lst in all_lists:
        entry = repo.get(lst.id)
        with Pool(50) as pool:
            new_files = pool.map(enrich_file_entry, entry.files)

        enriched_list = entry._replace(files=new_files)
        repo.put(enriched_list)
    end = time.time_ns()
    print(f'metadata update took {(end-start)/1000000000} seconds')


def async_enrichment(repo):
    job = Process(target=enrich_with_chapters, args=(repo,))
    job.start()
