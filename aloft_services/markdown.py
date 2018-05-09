from aloft_services import app
from werkzeug.exceptions import BadRequest, NotFound
from flask import request, render_template, make_response, jsonify
import mistune
import git
import os.path as osp
import os
import time
import tempfile

author = git.Actor('Someone', 'someone@localhost')
committer = git.Actor('Application', 'application@localhost')

time_format = '%m-%d-%y (%H:%M:%S)'
repo_dir = osp.normpath(osp.join(os.getcwd(), 'backend-repo/'))

if not osp.exists(repo_dir):
    repo = git.Repo.init(repo_dir)
else:
    repo = git.Repo(repo_dir)

def get_tags_for_file(filename):
    return sorted(
        [tag for tag in repo.tags if filename+'/' in tag.name],
        key = lambda t: t.name
    )

def get_commit_for_fileversion(filename, version):
    try:
        return repo.tags[filename+'/'+str(version)].commit
    except IndexError:
        raise NotFound('No file {} found in repository.'.format(filename))

def get_latest_data(filename):
    #filename = osp.split(filename)[-1]
    all_tags = get_tags_for_file(filename)
    if len(all_tags) == 0:
        raise NotFound('No file {} found in repository.'.format(filename))

    latest_commit = all_tags[-1].commit

    #print("Reading commit {} from tag {}".format(latest_commit, latest_tag.name))
    data = latest_commit.tree[filename].data_stream.read()

    return data.decode('utf-8')

def write_md_file(filename, data):
    #filename = osp.split(filename)[-1]
    new_path = osp.normpath(osp.join(repo_dir, filename))

    if not repo_dir in new_path:
        raise BadRequest('Cannot create file {} in repository.'.format(filename))

    base, fn = osp.split(new_path)
    if not osp.exists(base):
        os.makedirs(base)

    with open(new_path, 'w') as f:
        f.write(data)

    repo.index.add([new_path])
    commit = repo.index.commit('Update to {} at {} ({} bytes)'.format(
        filename, time.strftime(time_format), len(data)
    ), author=author, committer=committer)

    next_tag_idx = len(get_tags_for_file(filename))
    repo.create_tag(filename+'/'+str(next_tag_idx), ref=commit)

    return data

def read_md_file(filename, version=-1):
    #filename = osp.split(filename)[-1]

    if version < 0:
        return get_latest_data(filename)
    else:
        commit = get_commit_for_fileversion(filename, version)
        return commit.tree[filename].data_stream.read().decode('utf-8')

def summarize_commit(c):
    return {
        'author': {'name': c.author.name, 'email': c.author.email},
        'authored': c.authored_datetime.isoformat(),
        'committer': {'name': c.committer.name, 'email': c.committer.email},
        'committed': c.committed_datetime.isoformat(),
        'stats': c.stats.total,
        'summary': c.summary,
        'parents': [parent.hexsha for parent in c.parents],
        'sha': c.hexsha
    }

@app.route('/writing', methods=['POST'])
def new_writing():
    return mistune.markdown(write_md_file(
        request.form.get('filename'), request.form.get('text')
    ))

@app.route('/writing/info/<path:filename>')
def get_metadata(filename):
    tags = get_tags_for_file(filename)
    ret_data = []

    for i, tag in enumerate(tags):
        summary = summarize_commit(tag.commit)
        summary.update({
            'tag': tag.name,
            'version': i
        })

        ret_data.append(summary)

    return jsonify(ret_data)

@app.route('/writing/latest/<path:filename>', methods=['GET'])
def read_markdown(filename):
    return mistune.markdown(read_md_file(filename))

@app.route('/writing/latest/<path:filename>', methods=['POST'])
def update_markdown(filename):
    return mistune.markdown(write_md_file(
        filename, request.get_data(as_text=True)
    ))

@app.route('/writing/past/<int:version>/<path:filename>', methods=['GET'])
def read_past_markdown(version, filename):
    return mistune.markdown(read_md_file(filename, version))

@app.route('/writing/raw/latest/<path:filename>', methods=['GET'])
def read_raw_markdown(filename):
    return read_md_file(filename), {'Content-Type': 'text/markdown'}

@app.route('/writing/raw/past/<int:version>/<path:filename>', methods=['GET'])
def read_past_raw_markdown(version, filename):
    return read_md_file(filename, version), {'Content-Type': 'text/markdown'}
