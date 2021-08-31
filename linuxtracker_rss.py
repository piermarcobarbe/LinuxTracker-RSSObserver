from requests import get
from datetime import datetime
import xml.etree.ElementTree as ET
from json import dumps
import urllib.parse as urlparse
from urllib.parse import parse_qs
from os.path import isdir, join
import urllib3
from os import makedirs, getenv
from dotenv import load_dotenv
from importlib import import_module
import logging

logging_domain = "linuxtracker_RSS"

_nameToLevel = {
	'CRITICAL': logging.CRITICAL,
	'FATAL': logging.FATAL,
	'ERROR': logging.ERROR,
	'WARN': logging.WARNING,
	'WARNING': logging.WARNING,
	'INFO': logging.INFO,
	'DEBUG': logging.DEBUG,
	'NOTSET': logging.NOTSET,
}


def log(level, message):
	logger = logging.getLogger(logging_domain)
	logger.log(level=level, msg=message)


def create_path_if_necessary(path, dry_run=False):
	log(logging.DEBUG, "create_path_if_necessary({})".format(path))
	if path is None:
		log(logging.DEBUG, "Not creating path since it equals None.")
		return False
	if not isdir(path):
		log(logging.DEBUG, "Creating new path {}.".format(path))
		if not dry_run:
			makedirs(path)
		log(logging.INFO, "Created path {}.".format(path))
		return True
	log(logging.DEBUG, "Path {} already exists.".format(path))
	return False


def get_session_filename():
	log(logging.DEBUG, "get_session_filename()")
	now = datetime.now()
	date_str = datetime.strftime(now, "%d_%m_%Y-%H:%m:%S:%s")
	log(logging.DEBUG, "Session filename: {}".format(date_str))
	return date_str


def get_rss_content(alternative_url=None, tls_verify=True, dry_run=False):
	log(logging.DEBUG, "get_rss_content(alternative_url={}, tls_verify={})".format(alternative_url, tls_verify))

	rss_url = "https://linuxtracker.org/rss_torrents.php?pid=86a37955da34b675cc7aa36d351e7794"

	if alternative_url is not None:
		rss_url = alternative_url

	log(logging.INFO, "Using URL {} as RSS source".format(rss_url))
	if not dry_run:
		response = get(url=rss_url, verify=tls_verify)
		return response.content
	return "dry_run response".encode()


def get_rss_file(alternative_url=None, xml_download_dir=None, rss_filename=None, tls_verify=True, dry_run=False):
	log(logging.DEBUG, "get_rss_file(alternative_url={}, xml_download_dir={}, rss_filename={}, tls_verify={})".format(
		alternative_url, xml_download_dir, rss_filename, tls_verify
	))
	if xml_download_dir is None:
		xml_download_dir = "./"
	log(logging.DEBUG, "Using XML download directory './'")

	rss_content = get_rss_content(alternative_url=alternative_url, tls_verify=tls_verify, dry_run=dry_run)

	if rss_filename is None:
		rss_filename = get_session_filename() + ".xml"

	create_path_if_necessary(xml_download_dir, dry_run=dry_run)

	rss_filename = join(xml_download_dir, rss_filename).replace('/', '_')

	log(logging.INFO, "Saving RSS content into {}".format(rss_filename))

	if not dry_run:
		with open(rss_filename, 'wb') as fp:
			fp.write(rss_content)

	log(logging.INFO, "Saved RSS feed into {}".format(rss_filename))
	return rss_filename


def get_torrent_URLs_from_xml_tree(XML_Node, verbose=False):
	log(logging.DEBUG, "get_torrent_URLs_from_xml_tree({}, verbose={}"
		.format(XML_Node, verbose))
	urls = []
	for child in XML_Node:
		if child.tag == "enclosure":
			if verbose:
				print(child.attrib)
			if child.attrib.get('url') is not None:
				urls.append(child.attrib.get('url'))
				log(logging.DEBUG, "Added url {}".format(child.attrib.get('url')))
		else:
			urls += get_torrent_URLs_from_xml_tree(child, verbose=verbose)
	return urls


def download_from_url(url, download_dir=None, filename=None, filename_url_param=None, tls_verify=True):
	log(logging.DEBUG, "download_from_url(url={}, download_dir={}, filename={}, filename_url_param={}, tls_verify={}"
		.format(url, download_dir, filename, filename_url_param, tls_verify))
	if download_dir is None:
		download_dir = "./"
	log(logging.DEBUG, "Using download directory {}".format(download_dir))

	if filename_url_param is None:
		filename_url_param = 'f'

	parsed = urlparse.urlparse(url)
	if filename is None:
		filename = parse_qs(parsed.query)[filename_url_param][0]
		filename = str(filename)

	if filename is None:
		raise Exception("download_from_url: No filename specified")

	filename = join(download_dir, filename)

	log(logging.DEBUG, "Downloading {}...".format(filename))

	with get(url, verify=tls_verify) as response:
		with open(filename, 'wb') as fp:
			fp.write(response.content)
			log(logging.INFO, "Saved file at {}".format(filename))

	return filename


def download_torrents_from_url(url_list, torrent_download_path=None, tls_verify=True, verbose=False):
	if torrent_download_path is None:
		torrent_download_path = "./"
	log(logging.INFO, "Using torrent download path {}".format(torrent_download_path))

	if url_list is None:
		raise Exception("download_torrents_from_url: No url_list specified")

	create_path_if_necessary(torrent_download_path)

	created_files = []

	for url in url_list:
		created_file_path = download_from_url(url, download_dir=torrent_download_path, tls_verify=tls_verify)
		created_files.append(created_file_path)

	log(logging.INFO, "Saved {} files.".format(len(url_list)))

	return created_files


def main():
	load_dotenv()

	LINUXTRACKER_RSS_URL = getenv("LINUXTRACKER_RSS_URL")
	LINUXTRACKER_XML_DIRECTORY = getenv("LINUXTRACKER_XML_DIRECTORY") or "./"
	LINUXTRACKER_TORRENT_DIRECTORY = getenv("LINUXTRACKER_TORRENT_DIRECTORY") or "./"
	LINUXTRACKER_LOGGING_DIR = getenv("LINUXTRACKER_LOGGING_DIR")
	DISABLE_REQUESTS_WARNING = getenv("DISABLE_REQUESTS_WARNING") is not None
	NO_TLS_VERIFICATION = getenv("NO_TLS_VERIFICATION") is not None  # if variable is set, it will be set to True
	LINUXTRACKER_LOGGING_LEVEL = getenv("LINUXTRACKER_LOGGING_LEVEL") or "ERROR"
	LINUXTRACKER_DRY_RUN = getenv("LINUXTRACKER_DRY_RUN_SET") is not None
	LINUXTRACKER_HANDLER_FILE = getenv("LINUXTRACKER_HANDLER_FILE")
	LINUXTRACKER_HANDLER_CLASS = getenv("LINUXTRACKER_HANDLER_CLASS")

	if LINUXTRACKER_LOGGING_LEVEL in list(_nameToLevel.keys()):
		LINUXTRACKER_LOGGING_LEVEL = _nameToLevel[LINUXTRACKER_LOGGING_LEVEL]
	else:
		LINUXTRACKER_LOGGING_LEVEL = logging.DEBUG

	session_filename = get_session_filename()
	logging_format = "%(asctime)s\t%(levelname)s\t%(message)s"

	logging_config = {
		"level": LINUXTRACKER_LOGGING_LEVEL,
		"format": logging_format
	}

	logger = logging.getLogger(logging_domain)
	logger.setLevel(logging_config['level'])
	formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')

	if LINUXTRACKER_LOGGING_DIR is not None:
		create_path_if_necessary(LINUXTRACKER_LOGGING_DIR)
		logging_filename = session_filename + '.log'
		logging_filename = join(LINUXTRACKER_LOGGING_DIR, logging_filename)
		logging_config['filename'] = logging_filename
		logging_config['filemode'] = 'w'
		fh = logging.FileHandler(logging_config['filename'])
		fh.setLevel(logging_config["level"])
		fh.setFormatter(formatter)
		logger.addHandler(fh)

	ch = logging.StreamHandler()
	ch.setLevel(logging_config['level'])
	ch.setFormatter(formatter)

	logger.addHandler(ch)
	logger.propagate = False

	# logger.log(level=logging.DEBUG, msg="DEBUGGING")

	log(logging.DEBUG, "Configuration: " + dumps({
		"RSS_URL": LINUXTRACKER_RSS_URL,
		"XML_DIR": LINUXTRACKER_XML_DIRECTORY,
		"TORRENT_DOWNLOAD_DIR": LINUXTRACKER_TORRENT_DIRECTORY,
		"LOG_DIR": LINUXTRACKER_LOGGING_DIR,
		'DISABLE_REQUESTS_WARNING': DISABLE_REQUESTS_WARNING,
		"DISABLE_HTTP_TLS_VERIFICATION": NO_TLS_VERIFICATION,
		"LOGGING_LEVEL": LINUXTRACKER_LOGGING_LEVEL,
		"HANDLER_FILE": LINUXTRACKER_HANDLER_FILE,
		"HANDLER_CLASS": LINUXTRACKER_HANDLER_CLASS
	}, indent=4))

	if DISABLE_REQUESTS_WARNING:
		urllib3.disable_warnings()
		log(logging.DEBUG, "Disabled requests warning.")

	NO_TLS_VERIFICATION = not NO_TLS_VERIFICATION  # Since requests is asking if forcing verification or nots
	rss_filename = get_rss_file(alternative_url=LINUXTRACKER_RSS_URL,
								xml_download_dir=LINUXTRACKER_XML_DIRECTORY,
								tls_verify=NO_TLS_VERIFICATION,
								rss_filename=session_filename + ".xml",
								dry_run=LINUXTRACKER_DRY_RUN)

	if LINUXTRACKER_HANDLER_FILE is None or LINUXTRACKER_HANDLER_CLASS is None:
		log(logging.WARNING, "No handler file or class specified.")

	created_file_paths = []

	if not LINUXTRACKER_DRY_RUN:
		XML_Tree = ET.parse(rss_filename)
		torrents_urls = get_torrent_URLs_from_xml_tree(XML_Tree.getroot())
		log(logging.INFO, "Found {} torrent URLs".format(len(torrents_urls)))

		created_file_paths = download_torrents_from_url(torrents_urls,
														torrent_download_path=LINUXTRACKER_TORRENT_DIRECTORY,
														tls_verify=NO_TLS_VERIFICATION)

		log(logging.DEBUG, "Created files: " + ', '.join(created_file_paths))

	else:
		log(logging.INFO, "No files created since dry run mode is activated.")

	Module = import_module(LINUXTRACKER_HANDLER_FILE)
	Handler = getattr(Module, LINUXTRACKER_HANDLER_CLASS)
	# print(Handler)

	handler = Handler(log_function=log)
	handler.handle(created_file_paths, LINUXTRACKER_DRY_RUN)


if __name__ == "__main__":
	main()
