ROUTEBASE := 2003:1234::/32
# 4M /64 in /42, 2M /64 in /43
RB10 := 2003:aaaa:aa00::/42
RB11 := 2003:bbbb:bb00::/42
RB12 := 2003:cccc:cc00::/42
ROUTESUBLEN := 64
ROUTENH := fc00::20

MAXROUTES := 2500000
AS_MPATH := 20,1000
AS_ONEPATH := 20,100,200,300
AS_STPATH := 100,200,50000
MRTPEER := 10.0.0.30,fc00::30,30
STDARGS := -m $(MAXROUTES) $(ROUTEBASE) $(ROUTESUBLEN) $(ROUTENH)

# Names upd-<as-modcount>-<maxpack>-
# mod 0 means all unique AS numbers
# mod N means N unique AS paths
# maxpack number of NLRI per Update (will share attributes)
MSUPDFILES := mpath-0-1     mpath-100-1     mpath-1000-1 \
              mpath-0-10    mpath-100-10    mpath-1000-10 \
              mpath-0-1000  mpath-100-1000  mpath-1000-1000
OSUPDFILES := onepath-0-1 onepath-0-10 onepath-0-1000
SMRTFILES := st-10 st-11 st-12

MUPDFILES := $(patsubst %,data/%.raw,$(MSUPDFILES))
OUPDFILES := $(patsubst %,data/%.raw,$(OSUPDFILES))
MRTFILES := $(patsubst %,data/%.mrt,$(SMRTFILES))
CONFFILES := $(patsubst %,data/%-static.conf,$(SMRTFILES))

all:

clean:
	rm -f data/*.raw data/*.mrt data/*.conf

conf: $(CONFFILES)

upd: $(OUPDFILES) $(MUPDFILES)

setup:
	test -d venv || (python3 -m venv venv; echo $$(pwd)/venv > .venv)
	. venv/bin/activate && pip install -r requirements.txt

# -------------------
# Static Route Config
# -------------------

data/st-10-static.conf:
	AS=10; ./genrt.py --dump-format "    route {prefix} blackhole;" \
                    -f $@ 2100::/13 32 fc$${AS}::$${AS} \
                          2110::/21 40 fc$${AS}::$${AS} \
                          2120::/28 48 fc$${AS}::$${AS} \
                          2130::/45 64 fc$${AS}::$${AS}

data/st-11-static.conf: data/st-10-static.conf
	sed -e 's/route 21/route 22/; s,fc10::1,fc20::1,' < data/st-10-static.conf > data/st-11-static.conf

data/st-12-static.conf: data/st-10-static.conf
	sed -e 's/route 21/route 23/; s,fc10::1,fc30::1,' < data/st-10-static.conf > data/st-12-static.conf

# ------------------
# Raw Update Message
# ------------------

$(MUPDFILES): FORCE
	bash -c 'T1=$@; T2=$${T1#data/}; T=$${T2%.raw}; ARGS=$${T#mpath-}; MPACK=$${ARGS#*-}; MOD=$${ARGS%-*}; ./genrt.py -u $$T1 --root-as-inc --root-as-mod=$$MOD --aspath $(AS_MPATH) --max-pack $$MPACK \
    2100::/13 32 fc$${AS}::$${AS} \
    2110::/21 40 fc$${AS}::$${AS} \
    2120::/28 48 fc$${AS}::$${AS} \
    2130::/45 64 fc$${AS}::$${AS}'

$(OUPDFILES): FORCE
	bash -c 'T1=$@; T2=$${T1#data/}; T=$${T2%.raw}; ARGS=$${T#onepath-}; MPACK=$${ARGS#*-}; ./genrt.py -u $@ --aspath $(AS_ONEPATH) --max-pack $$MPACK \
    2100::/13 32 fc$${AS}::$${AS} \
    2110::/21 40 fc$${AS}::$${AS} \
    2120::/28 48 fc$${AS}::$${AS} \
    2130::/45 64 fc$${AS}::$${AS}'


# ------------------------------------------------
# MRT Tables (used with GoBGP - not used too slow)
# ------------------------------------------------

mrt: $(MRTFILES)

data/st-10.mrt:
	AS=10; ./genrt.py -t $@ -p $(MRTPEER) --root-as-inc --aspath $${AS},${AS_STPATH} --max-pack 1 -m $(MAXROUTES) $(RB10) $(ROUTESUBLEN) fc$${AS}::$${AS}

data/st-11.mrt:
	AS=11; ./genrt.py -t $@ -p $(MRTPEER) --root-as-inc --aspath $${AS},${AS_STPATH} --max-pack 1 -m $(MAXROUTES) $(RB11) $(ROUTESUBLEN) fc$${AS}::$${AS}

data/st-12.mrt:
	AS=12; ./genrt.py -t $@ -p $(MRTPEER) --root-as-inc --aspath $${AS},${AS_STPATH} --max-pack 1 -m $(MAXROUTES) $(RB12) $(ROUTESUBLEN) fc$${AS}::$${AS}

FORCE:

