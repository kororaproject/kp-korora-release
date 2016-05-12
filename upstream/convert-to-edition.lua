-- This is intended to be run as an RPM scriptlet.
-- Keep this file in sync with the convert-to-edition
-- shell script

local VARIANT_FILE = "/usr/lib/variant"

-- Read in /usr/lib/variant and determine the edition
local function read_variant()
  local variant
  local f = io.open(VARIANT_FILE, "r")
  if f ~= nil then
    while true do
      local line = f:read()
      if line == nil then
        break
      end
      local m = line:match("^VARIANT_ID=([^\n]+)")
      if m ~= nil then
        variant = m
      end
    end
    f:close()
  end
  return variant
end

-- Atomically replace a file with new contents
local function writefile(path, data)
  local tmp = path .. ".convert-to-edition"
  local f = io.open(tmp, "w+")
  if f == nil then
    return
  end
  f:write(data)
  f:close()
  if not os.rename(tmp, path) then
    os.remove(tmp)
  end
end

-- Forcibly replace a symlink
local function symlink(from, to)
  os.remove(to)
  assert(posix.symlink(from, to))
end

-- Run a subroutine in a child process
local function execute(...)
  local pid = posix.fork()
  if pid == 0 then
    posix.exec(...)
    posix.exit(1)
  elseif pid ~= -1 then
    local status = posix.wait(pid)
    if status ~= 0 then
      local program = ...
      error(program .. " exited with status " .. status)
    end
  end
end

-- Remove preset files for other editions
-- This should never be necessary, but it's best to be safe
local function clear_presets()
  local path = "/usr/lib/systemd/system-preset"
  for file in posix.files(path) do
    if file:match("^80-.*%.preset$") then
      os.remove(path .. "/" .. file)
    end
  end
end


-- Get a list of presets that need to be enabled or disabled
-- as part of the installation of this edition
local function read_presets(path)
  local result = {}
  local f = assert(io.open(path))
  if f ~= nil then
    while true do
      local line = f:read()
      if line == nil then
        break
      end
      local cmd, arg = line:match("^([^ \t]+)[ \t]+([^\n \t]+)")
      if cmd == "enable" or cmd == "disable" then
        result[#result + 1] = arg
      end
    end
    f:close()
  end
  return result
end

local function set_variant(variant)
  writefile(VARIANT_FILE, "VARIANT_ID=" .. variant .. "\n")
end

local function set_release(release)
  symlink("./os.release.d/os-release-" .. release, "/usr/lib/os-release")
end

local function set_issue(release)
  symlink("./os.release.d/issue-" .. release, "/usr/lib/issue")
end
-- release: the VARIANT_ID for os-release
-- issue: which /etc/issue file to install
-- presets: whether this edition has extra presets beyond the
--          defaults to enable or disable
local variants = {
  atomichost = {release = "atomichost", issue = "fedora", presets = false},
  cloud = {release = "cloud", issue = "fedora", presets = false},
  nonproduct = {release = "fedora", issue = "fedora", presets = false},
  server = {release = "server", issue = "server", presets = true},
  workstation = {release = "workstation", issue = "fedora", presets = true},
}

-- Call out to systemctl to enable or disable presets
local function set_presets(edition, apply_presets)
  if variants[edition].presets then
    local target = "/usr/lib/systemd/system-preset/80-" .. edition .. ".preset"
    symlink("../../os.release.d/presets/80-" .. edition .. ".preset", target)

    if apply_presets then
      local presets = read_presets(target)
      local systemctl = "/usr/bin/systemctl"
      if posix.access(systemctl, "x") then
        --fork off a systemctl call
        local pid = assert(posix.fork())
        if pid == 0 then
          -- Child
          posix.exec(systemctl, "preset", "-q", table.unpack(presets))
          -- In case exec() fails
          os.exit(17)
        else
          -- RPM
          assert(posix.wait(pid))
        end
      end
    end
  end
end

local function convert_to_edition(edition, apply_presets)
  local variant = variants[edition]
  if variant == nil then
    error("undefined edition: " .. edition)
  end
  set_release(variant.release)
  set_issue(variant.issue)
  clear_presets()

  set_presets(edition, apply_presets)
end

local function install_edition(edition)
  -- Create the variant file if it does not already exist. This needs
  -- to be done on both installation and upgrade, to ensure that we
  -- upgrade from F23 and earlier properly.
  if not posix.access(VARIANT_FILE, "f") then
    set_variant(edition)
  end
  if read_variant() == edition then
    -- (On initial installation only), fix up after %%systemd_post
    -- in packages possibly installed before our preset file was
    -- added
    -- On upgrades, do not enable or disable presets to avoid
    -- surprising the user
    local initial_install = arg[2] == 1
    convert_to_edition(edition, initial_install)
  end
end

local function uninstall_edition(edition)
  -- If we are uninstalling, we need to reset the variant file and
  -- force the os-release file back to os-release-fedora.  We do this
  -- in %%preun so that we don't have any time where the os-release
  -- symlink is dangling (since in %%postun, the os-release-$EDITION
  -- file will have already been removed)
  if arg[2] == 0 then
    if read_variant() == edition then
      set_variant("nonproduct")
      convert_to_edition("nonproduct", false)
    end
  end
end
