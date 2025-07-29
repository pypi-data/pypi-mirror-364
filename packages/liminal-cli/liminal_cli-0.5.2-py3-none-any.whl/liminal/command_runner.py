import logging
import os
from pathlib import Path
import subprocess
import sys
import time
import pexpect
import uuid
from liminal.logging import LOGGER



def _ugh(shell_exec_path: str, timeout_seconds=3, env=None):
	shell_command = f"{shell_exec_path} -l"
	if env is None:
		env = os.environ.copy()
	
	print('child debug test start')
	child = pexpect.spawn(shell_command, encoding='utf-8', timeout=timeout_seconds, env=env)
	child.logfile = sys.stdout # use sys.stdout to more easily debug (see output as it is occuring)

	child.expect([pexpect.EOF, pexpect.TIMEOUT])
	child.close()

	print('child debug test ended')
	print(child.before)
	print('---')
	print(child.after)

	return child



def _create_and_match_prompt(process: pexpect.spawn, ) -> str:
	""""""
	uniquePS1 = f'_lm_{uuid.uuid4()}_prompt__'
	export_command = f"export PS1={uniquePS1}   "
	search_attempt = 0
	max_attempts = 4

	process.sendline(export_command)
	# sometimes the export_command is sent before the shell has finished loading, and so welcome message appears before it
	while True:
		LOGGER.debug(f'trying to match PS1 {search_attempt=}')
		try:
			process.expect(f'export PS1={uniquePS1}   .*{uniquePS1}', timeout=1) # be a bit slower to wait for startup messages
			return uniquePS1
		except pexpect.TIMEOUT:
			search_attempt += 1
		if search_attempt >= max_attempts:
			break
	raise Exception(f'Couldnt run login command due to unexpected PS1 parsing issue. {process.before=} {process.after=}')


TEST_COMMAND_PREFIX = 'logger "liminal_test'

def run_test_login_command(shell_exec_path: str | Path, key: str, env=None) -> tuple[str, str | None]:
	full_cmd = f'{TEST_COMMAND_PREFIX} {key}"'
	return full_cmd, run_login_command(str(shell_exec_path), full_cmd, env=env)


def run_login_command(shell_exec_path: str, cmd: str, timeout_seconds=3, env=None):
	"""
	this seems to be the only way to run a command from python and have atuin record it

	since someone's PS1 can contain anything and/or be dynamic (like mine), we temporarily set PS1 as a uuid we generate
	so we can match between them to get the exact command output
	
	subprocess.run(['bash', '-ic', 'mycommand; exit']) doesnt work
		# resp = subprocess.run(['bash', '-ic', f'logger "liminal installed {datetime_utcnow()} {uuid4()}"'])
		resp = subprocess.run(['bash', '-ic', f'eval "$(atuin init bash)"; echo pleaseeee; true; exit 0'], cwd=Path(__file__).parent.parent, env=None)

	other potential strategies: 
		- send noop, diff before and after content to determine PS1
		- check if there is a way to do it with `-c` and still get atuin to work, maybe just needs proper env vars
	"""

	shell_command = f"{shell_exec_path} -l"
	LOGGER.info(f"{shell_exec_path} -l '{cmd}'")
	if env is None:
		env = os.environ.copy()
	child = pexpect.spawn(
		shell_command,
		encoding='utf-8', timeout=12+timeout_seconds+1, env=env,
		dimensions=(100, 500) # WARNING: this is important, if not large enough, text will be truncated, causing matches to fail
	)
	# child.delaybeforesend = 0.1 # maybe this will help with unexpected timeouts/matches
	# child.logfile = sys.stdout # use sys.stdout to more easily debug (see output as it is occuring)

	try:
		uniquePS1 = _create_and_match_prompt(child)
		LOGGER.debug(f'sucessfully set {uniquePS1=}')
		# now we can match our newly set prompt
		child.sendline(cmd)
		child.expect_exact(uniquePS1, timeout=timeout_seconds)
		raw_cmd_output = child.before
		return raw_cmd_output
	finally:
		child.terminate()
		child.close()


def run_command(cmd: list, cmd_output_log_level=logging.DEBUG, logger=LOGGER, check=True, **kwargs) -> subprocess.CompletedProcess[str]:
	logger.debug(f'Running command: {cmd}')
	try:
		task = subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)
	except subprocess.CalledProcessError as e:
		logger.error(f'Error running command: {cmd}')
		logger.info(e.stdout)
		logger.info(e.stderr)
		raise e

	logger.log(cmd_output_log_level, task.stdout)
	logger.log(cmd_output_log_level, task.stderr)


	if task.returncode != 0:
		msg = f'Error running command: {task.returncode}: {cmd}'
		log_level = logging.WARNING
		if not check:
			log_level = logging.DEBUG
		logger.log(log_level, msg)
		logger.debug(task.stdout)
		logger.debug(task.stderr)
	else:
		logger.debug(f'Finished command: {cmd}')

	return task


if __name__ == '__main__':
	import sys
	from liminal.shell import Shell
	try:
		timeout = int(sys.argv[2])
	except (IndexError, TypeError, ValueError):
		timeout=3
	# TODO: we need to set a different LOGGER here
	output = run_login_command(Shell().exec_path.as_posix(), sys.argv[1], timeout_seconds=timeout)
	print(output)
