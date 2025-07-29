import os

from liminal import LIMINAL_DIR

class Config:
	API_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_API_ADDRESS', 'https://shellsync.liminalbios.com/api/v1')
	SYNC_ADDRESS = os.environ.get('LIMINAL_SHELLSYNC_ATUIN_ADDRESS', 'https://atuin.services.shellsync.liminalbios.com')

	LIMINAL_INSTALLER_SKIP_CLEANUP = os.environ.get('LIMINAL_INSTALLER_SKIP_CLEANUP', 'no').strip().lower()
	LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT_HISTORY = os.environ.get('LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT', None)
	LIMINAL_INSTALLER_PAUSE_AT = os.environ.get('LIMINAL_INSTALLER_PAUSE_AT', '').strip()
	LIMINAL_INSTALLER_ATUIN_HISTORY_SEED_FILE = os.environ.get('LIMINAL_INSTALLER_ATUIN_HISTORY_SEED_FILE', None)

def write(key: str, value):
	# TODO: xdg base dirs
	# TODO: real config file
	(LIMINAL_DIR / 'config').write_text(value)

def read(key: str):
	return (LIMINAL_DIR / 'config').read_text()
