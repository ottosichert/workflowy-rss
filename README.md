# RSS API for Workflowy

WorkFlowy currently does not provide any public API. There are some existing 3rd party implementations for various but minimal access to your WorkFlowy items, however none of them allowed filtering for overdue items using the [Dates feature](https://blog.workflowy.com/2019/12/30/dates-in-workflowy-try-it-out/). Relevant links:

- Request for a public API: https://workflowy.zendesk.com/hc/en-us/community/posts/201100295-API
- PHP API: https://github.com/johansatge/workflowy-php
- CLI: https://github.com/malcolmocean/opusfluxus

# Usage

To use this RSS API, you will need a WorkFlowy `sessionid`. You can obtain this by going to https://workflowy.com/ and inspecting the network tabs and copying it out of the request cookies. Otherwise you can use the `opusfluxus` CLI above and copy it out of the `~/.wfrc` file after running the command `wf` once and authenticating through it.

Then, you can use any RSS reader to view your overdue WorkFlowy items. For example on iOS, you can use this app: https://apps.apple.com/us/app/my-widgets/id885234948. It provides an iOS widget 'Quote of the Day' for `1.09€`. If you find any alternative that works, please let me know as this app requires a small workaround (only shows one item).

# API

The API is hosted at https://workflowy-rss.now.sh. It accepts the `sessionid` mentioned above as GET parameter. By default the timezone `Europe/Stockholm` will be used. To override this, pass the `timezone` GET parameter in your request.

Currently, there is only one endpoint, `/overdue`, with a minimal set of options.

## `/overdue`

| Name | Usage   | Description |
|------|---------|-------------|
| **summary** | `summary` | Lists the total number of overdue items |
| **index** | `index=0` | Shows the n-th entry of overdue items. Negative values are also allowed, e.g. `-1` for the last item |

If no additional parameter is given, the full list of overdue items is returned.

# Examples

- `/overdue?session_id=foobar&index=3`: Returns the 4th overdue item
- `/overdue?session_id=foobar&summary&timezone=America/New_York`: Returns the number of overdue items until midnigth in New York
- `/overdue?session_id=foobar`: Returns a list of all overdue items
