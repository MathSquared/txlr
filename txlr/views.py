from flask import redirect, render_template, request

from . import app
from .redirectors import REDIRECTORS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/go')
def go():
    q = request.args.get('q')

    results = [redir(q) for redir in REDIRECTORS]
    messages = []
    for redir, res in zip(REDIRECTORS, results):
        if res[0] == True:
            return redirect(res[1], code=303)
        else:
            messages.append((
                res[1],
                redir.__name__,
                getattr(redir, 'title', None),
                getattr(redir, 'pattern', None),
            ))

    # TODO format errors better
    return repr(messages), 404
