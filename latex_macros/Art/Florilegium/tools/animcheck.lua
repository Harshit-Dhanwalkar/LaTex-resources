-- Check that the growth animation ends on exactly the page: for each seed, the
-- last frame of the recording must equal the normal page byte for byte (with and
-- without the spill under the text; in summer, in spring, and in autumn with a
-- heading and a \florilegiumbloom marked in the text). Runs without TeX:
--   texlua tools/animcheck.lua 1 2 3      (or: tools/in-docker texlua tools/animcheck.lua)
tex = { sprint = function() end }
luatexbase = { registernumber = function() return 0 end }
local out
node = { new = function() return {} end, write = function(n) out = n.data end }
package.path = "./?.lua;" .. package.path
local ink, grow = require("ink"), require("grow")

-- an A4 page with a 68 mm left margin, roughly as in the demo documents
local CASES = {
  { name = "summer" },
  { name = "spring", age = 0.05 },
  { name = "autumn, marks", age = 0.95, marks = { { kind = "heading", arg = 1, y = 20 }, { kind = "bloom", arg = "", y = 9 } } },
}
local function geometry(seed, spill, case)
  local g = { pw = 21, ph = 29.7, textleft = 6.8, textright = 18.8, ytop = 25.4, ybot = 3.0 }
  g.colright, g.headrule, g.footy = g.textleft - 0.4, g.ytop + 0.7, 1.9
  g.seed, g.spill, g.spilly = seed, spill, spill == 1 and 19.0 or 0
  g.age, g.marks = case.age, case.marks
  return g
end

local seeds = {}
for _, a in ipairs(arg) do seeds[#seeds + 1] = tonumber(a) end
if #seeds == 0 then seeds = { 1, 2, 3, 7 } end
local bad = 0
for _, seed in ipairs(seeds) do
  for _, spill in ipairs({ 0, 1 }) do for _, case in ipairs(CASES) do
    grow.page(geometry(seed, spill, case))
    local page = out
    local g = geometry(seed, spill, case)
    g.anim = true
    local r = grow.page(g)
    ink.emit(r.rec, function(tag)
      if tag.overlay then return false end
      local e = tag[1]
      local p = (math.huge - e.t0) / e.dur           -- as florilegium.lua does for the last frame
      return p >= tag[2] and (tag[3] == nil or p < tag[3])
    end)
    local ok = out == page
    if not ok then bad = bad + 1 end
    print(string.format("\nseed %d, spill %d, %s: %s (%.0f KB, %.1f s of growth)", seed, spill, case.name,
      ok and "last frame = page" or "LAST FRAME DIFFERS", #page / 1024, r.total))
  end end
end
os.exit(bad == 0 and 0 or 1)
