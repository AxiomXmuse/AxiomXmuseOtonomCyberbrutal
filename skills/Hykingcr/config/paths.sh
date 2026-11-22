# Resolve hangX paths. Prefer machine-local file written by install.sh.
_HYKINGCR_CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$_HYKINGCR_CONFIG_DIR/local-paths.env" ]]; then
  # shellcheck disable=SC1091
  source "$_HYKINGCR_CONFIG_DIR/local-paths.env"
fi
: "${HANGX_ROOT:=$HOME/hangX}"
: "${OMP_REPOS_ROOT:=$HANGX_ROOT/repos}"
: "${HANGX_JAIL_ROOT:=$HANGX_ROOT/vendor/jail/skills}"
: "${SECLISTS_ROOT:=$HOME/tools/SecLists}"
: "${BURP_ROOT:=$HOME/tools/BurpSuiteCommunity}"
: "${CERTIPY_BIN:=$HOME/.local/bin/certipy}"
: "${NETEXEC_BIN:=$HOME/.local/bin/netexec}"
