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

from handlers.TransmissionHandler import TransmissionHandler


def create_path_if_necessary(path):
	if path is None:
		return False
	if not isdir(path):
		makedirs(path)
		return True
	return False


def get_rss_filename():
	now = datetime.now()
	date_str = datetime.strftime(now, "%d_%m_%Y-%H:%m:%S:%s.xml")
	return date_str


def get_rss_content(alternative_url=None, tls_verify=True, verbose=False):
	if verbose:
		print({
			'fn': "get_rss_content",
			"alternative_url": alternative_url,
			"tls_verify": tls_verify
		})

	rss_url = "https://linuxtracker.org/rss_torrents.php?pid=86a37955da34b675cc7aa36d351e7794"

	if alternative_url is not None:
		rss_url = alternative_url

	response = get(url=rss_url, verify=tls_verify)
	return response.content


def get_rss_file(alternative_url=None, xml_download_dir=None, tls_verify=True, verbose=False):
	if xml_download_dir is None:
		xml_download_dir = "./"

	if verbose:
		print({
			"fn": "get_rss_file",
			"alternative_url": alternative_url,
			"xml_download_dir": xml_download_dir,
			"tls_verify": tls_verify
		})

	if alternative_url is not None:
		rss_content = get_rss_content(alternative_url=alternative_url, tls_verify=tls_verify, verbose=verbose)
	else:
		rss_content = get_rss_content(alternative_url=alternative_url, tls_verify=tls_verify, verbose=verbose)

	rss_filename = get_rss_filename()

	create_path_if_necessary(xml_download_dir)

	rss_filename = join(xml_download_dir, rss_filename)

	with open(rss_filename, 'wb') as fp:
		fp.write(rss_content)

	return rss_filename


def get_torrent_URLs_from_xml_tree(XML_Node, verbose=False):
	urls = []
	for child in XML_Node:
		if child.tag == "enclosure":
			if verbose:
				print(child.attrib)
			if child.attrib.get('url') is not None:
				urls.append(child.attrib.get('url'))
		else:
			urls += get_torrent_URLs_from_xml_tree(child, verbose=verbose)
	return urls


def download_from_url(url, download_dir=None, filename=None, filename_url_param=None, tls_verify=True, verbose=False):
	if download_dir is None:
		download_dir = "./"

	if filename_url_param is None:
		filename_url_param = 'f'

	parsed = urlparse.urlparse(url)
	if filename is None:
		filename = parse_qs(parsed.query)[filename_url_param][0]

	if filename is None:
		raise Exception("download_from_url: No filename specified")

	filename = join(download_dir, filename)

	if verbose:
		print("Downloading {}...".format(filename))

	with get(url, verify=tls_verify) as response:
		with open(filename, 'wb') as fp:
			fp.write(response.content)

	return filename


def download_torrents_from_url(url_list, torrent_download_path=None, tls_verify=True, verbose=False):
	if torrent_download_path is None:
		torrent_download_path = "./"

	if url_list is None:
		raise Exception("download_torrents_from_url: No url_list specified")

	create_path_if_necessary(torrent_download_path)

	created_files = []

	for url in url_list:
		created_file_path = download_from_url(url, download_dir=torrent_download_path, tls_verify=tls_verify,
											  verbose=verbose)
		created_files.append(created_file_path)

	return created_files


def main():
	verbose = False

	load_dotenv(verbose=verbose)

	RSS_URL = getenv("LINUXTRACKER_RSS_URL")
	XML_DIR = getenv("LINUXTRACKER_XML_DIRECTORY") or "./"
	TORRENT_DOWNLOAD_DIR = getenv("LINUXTRACKER_TORRENT_DIRECTORY") or "./"
	DISABLE_REQUESTS_WARNING = getenv("DISABLE_REQUESTS_WARNING") is not None
	NO_TLS_VERIFICATION = getenv("NO_TLS_VERIFICATION") is not None  # if variable is set, it will be set to True

	if verbose:
		print({
			'DISABLE_REQUESTS_WARNING': DISABLE_REQUESTS_WARNING,
			"DISABLE_HTTP_TLS_VERIFICATION": NO_TLS_VERIFICATION,
			"RSS_URL": RSS_URL,
			"XML_DIR": XML_DIR,
			"TORRENT_DOWNLOAD_DIR": TORRENT_DOWNLOAD_DIR
		})

	if DISABLE_REQUESTS_WARNING:
		urllib3.disable_warnings()

	NO_TLS_VERIFICATION = not NO_TLS_VERIFICATION  # Since requests is asking if forcing verification or not

	rss_filename = get_rss_file(RSS_URL, XML_DIR, tls_verify=NO_TLS_VERIFICATION, verbose=verbose)
	XML_Tree = ET.parse(rss_filename)
	torrents_urls = get_torrent_URLs_from_xml_tree(XML_Tree.getroot(), verbose)
	created_file_paths = download_torrents_from_url(torrents_urls, torrent_download_path=TORRENT_DOWNLOAD_DIR,
													tls_verify=NO_TLS_VERIFICATION, verbose=verbose)
	TransmissionHandler().handle(created_file_paths)


if __name__ == "__main__":
	main()
