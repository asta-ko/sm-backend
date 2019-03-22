#!/usr/bin/env bash

set -o errexit

echo "I am indempotent update script"

FLAG_APPLIED=0

check_applied() {
  if [ -f .test ]; then
    echo "Script already applied"
    FLAG_APPLIED=1
  else
    echo "Script will be applied"
  fi
}

apply_changes() {
  echo "Create test file"
  #this will remove .lock and testfile on error or interruption
  trap "rollback_changes; exit" INT TERM EXIT
  touch .lock
  sleep 10s
  touch .test
  rm -f .lock
  trap - INT TERM EXIT
}

rollback_changes() {
  rm -f .lock
  rm -f .test
}

main() {
  if [ $FLAG_APPLIED = 1 ]; then
      exit 0;
  elif [ $FLAG_APPLIED = 0 ]; then
    apply_changes
  else
    echo "Unknown error" && exit 1;
  fi

}

main "$@"
