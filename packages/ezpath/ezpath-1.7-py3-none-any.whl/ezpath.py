
import os
import sys
import glob
import fnmatch
import inspect

def get_abs_path(rel_path="", up=0, follow_links=False):
	'''
	Resolves the absolute path of <rel_path> relative to te parent directory
	of the caller's file

	Args:
		rel_path(str): path to be resolved, relative to the caller's file
		up           : the resulting path is <up>-times the parent directory of the original path
		follow_links : if True, symlinks are followed to the original source

	'''
	getpath = os.path.realpath if follow_links else os.path.abspath

	current_file = getpath(__file__)
	stack = inspect.stack()
	for frame in stack:
		caller = getpath(frame.filename)
		if caller != current_file:
			break

	file_path = os.path.dirname(getpath(caller))
	file_path = os.path.join(file_path, rel_path)
	ret_path  = getpath(file_path)

	for i in range(up):
		ret_path = os.path.dirname(ret_path)

	return ret_path


def add_abs_path(abs_path):
	'''
	Adds <abs_path> to PYTHONPATH
	'''
	if abs_path not in sys.path:
		sys.path += [abs_path]


def add_rel_path(rel_path, follow_links=False):
	'''
	Adds <rel_path> (relative to the caller's file) to PYTHONPATH
	'''
	add_abs_path(get_abs_path(rel_path, follow_links))


def join_path(*args):
	return os.path.join(*args)


def to_os_path(path, os_name=None):
	'''
	Converts any file/folder path to the appropriate format for the current OS
	'''
	if os_name == 'linux':
		sep = '/'
	elif os_name == 'windows':
		sep = '\\'
	else:
		sep = os.sep
	return path.replace('/', sep).replace('\\', sep)


def get_basename(path, up=0, noext=False):
	'''
	Gets the basename of a given path with the option to go up <up> levels and
	remove the file extension
	'''
	for i in range(up):
		path = os.path.dirname(path)
	path = os.path.basename(path)
	if noext:
		path = os.path.splitext(path)[0]
	return path


def find_root(dir=None, root_elem=[], root_name=[]):
	'''
	Finds a filesystem root directory relative to dir, based on:
	root_elem(List[str]) : list of possible file/folder name patterns found in the desired root
	root_name(List[str]) : list of possible name patterns for the root directory
	'''
	if dir is None:
		dir = os.getcwd()
	if isinstance(root_elem, str):
		root_elem = [root_elem]
	if isinstance(root_name, str):
		root_name = [root_name]

	root = os.path.abspath(dir)
	depth = 0
	while True:
		# name is always matched if no match patterns are selected
		name_match = len(root_name) == 0
		name_match |= any(fnmatch.fnmatch(os.path.basename(root), pat) for pat in root_name)

		# element is always matched if no match patterns are selected
		elem_match = len(root_elem) == 0
		for e in root_elem:
			elem = glob.glob(os.path.join(root, e), recursive=False)
			if len(elem) != 0:
				elem_match = True
				break

		if elem_match and name_match:
			break
		if depth >= 100:
			raise Exception(f"Maximum project depth ({depth}) reached")
		root = os.path.dirname(root)
		depth += 1
	return root
