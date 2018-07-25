
ROUTEBASE := 2003:1b3b:f000::/36
ROUTESUBLEN := 64
ROUTENH := fc00::20
MAXROUTES := 2500000
AS_MPATH := 20,1000
AS_ONEPATH := 20,100,200,300
STDARGS := -m $(MAXROUTES) $(ROUTEBASE) $(ROUTESUBLEN) $(ROUTENH)

# Names upd-<as-modcount>-<maxpack>-
MSUPDFILES := mpath-0-1     mpath-10-1     mpath-100-1 \
              mpath-0-10    mpath-10-10    mpath-100-10 \
              mpath-0-1000  mpath-10-1000  mpath-100-1000
OSUPDFILES := onepath-0-1 onepath-0-10 onepath-0-1000

MUPDFILES := $(patsubst %,data/%.raw,$(MSUPDFILES))
OUPDFILES := $(patsubst %,data/%.raw,$(OSUPDFILES))

all: $(OUPDFILES) $(MUPDFILES)

$(MUPDFILES): FORCE
	bash -c 'T1=$@; T2=$${T1#data/}; T=$${T2%.raw}; ARGS=$${T#mpath-}; MPACK=$${ARGS#*-}; MOD=$${ARGS%-*}; ./genrt.py -u $$T1 --root-as-inc --root-as-mod=$$MOD --aspath $(AS_MPATH) --max-pack $$MPACK $(STDARGS)'

$(OUPDFILES): FORCE
	bash -c 'T1=$@; T2=$${T1#data/}; T=$${T2%.raw}; ARGS=$${T#onepath-}; MPACK=$${ARGS#*-}; ./genrt.py -u $@ --aspath $(AS_ONEPATH) --max-pack $$MPACK $(STDARGS)'

FORCE:
