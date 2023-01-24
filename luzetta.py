import tidalapi
import argparse
import openpyxl


class DataEntry:
    autor_wpisu: ""
    category: ""
    composer: ""
    lyricist: ""
    artist: ""
    title: ""
    album: ""
    label: ""


def get_parser(h):
    parser = argparse.ArgumentParser(description='LUZetta tracklist processor.', add_help=h)
    parser.add_argument('-i', '--input', nargs=1, metavar='INPUT_FILE_PATH', help='Excel file path', required=False)
    parser.add_argument('-o', '--output', nargs=1, metavar='OUTPUT_PATH', help='Output file path', required=False)
    parser.add_argument('-f', '--filter', nargs=1, metavar='FILTER_STRING', help='Filter by author', required=False)

    return parser


def init_tidal_session():
    session = tidalapi.Session()
    # Will run until you visit the printed url and link your account
    session.login_oauth_simple()

    return session


def get_track_info(result):
    for track in result['tracks']:
        return track


def fetch_tidal_data(session, query):
    result = session.search(query=query, models=None, limit=50, offset=0)

    track_info = get_track_info(result)
    if track_info is not None:
        print("Track: " + track_info.artist.name + " - " + track_info.name
              + " [" + track_info.album.name + "][" + str(track_info.album.year) + "]")
        track_info_extended = session.track(track_info.id)
        album_info = session.album(track_info.album.id)
        page_info = album_info.page()
        for artist in track_info.artists:
            print("// (Artists : " + artist.name + ", " + artist.role.name + ")")


def process_input_data(input_data):
    workbook = openpyxl.load_workbook(input_data)
    sheet = workbook.active
    row = sheet.max_row
    column = sheet.max_column

    data_list = []

    autor_wpisu = 0
    category = 0
    composer = 0
    lyricist = 0
    artist = 0
    title = 0
    album = 0
    label = 0

    # Read and determine headers
    for i in range(1, column + 1):
        cell = sheet.cell(row=1, column=i)
        if cell.value == "Autor_wpisu":
            autor_wpisu = i
        elif cell.value == "Category":
            category = i
        elif cell.value == "Composer":
            composer = i
        elif cell.value == "Writer/Lyricist":
            lyricist = i
        elif cell.value == "Artist":
            artist = i
        elif cell.value == "Title":
            title = i
        elif cell.value == "Album":
            album = i
        elif cell.value == "Label":
            label = i

    # Read all the data
    for i in range(2, row + 1):
        data_entry = DataEntry()
        data_entry.autor_wpisu = get_sheet_value(sheet, i, autor_wpisu)
        data_entry.category = get_sheet_value(sheet, i, category)
        data_entry.composer = get_sheet_value(sheet, i, composer)
        data_entry.lyricist = get_sheet_value(sheet, i, lyricist)
        data_entry.artist = get_sheet_value(sheet, i, artist)
        data_entry.title = get_sheet_value(sheet, i, title)
        data_entry.album = get_sheet_value(sheet, i, album)
        data_entry.label = get_sheet_value(sheet, i, label)
        data_list.append(data_entry)

    print("Processed successfully: " + str(len(data_list)) + " entries")

    return data_list


def get_sheet_value(sheet, row, column):
    cell = sheet.cell(row=row, column=column)
    return cell.value


if __name__ == '__main__':
    # Define parser
    args_parser = get_parser(h=True)
    args = args_parser.parse_args()
    entries = []
    author_filter = ""

    if args.filter is not None:
        author_filter = args.filter[0]
    if args.input is not None:
        entries = process_input_data(args.input[0])
        tidal_session = init_tidal_session()
        for entry in entries:
            if author_filter == "" or entry.autor_wpisu == author_filter:
                fetch_tidal_data(tidal_session, entry.artist.split(" ft. ")[0] + " " + entry.title)

    print('luzetta-server: Processed successfully.')
