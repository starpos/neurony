#!/bin/sh

doPlotAccuracy()
{
local pngFileName=$1
local nameList="$2"

cat <<EOF
set yrange [0:80]
set key top left
set xlabel "Number of input charactors"
set ylabel "rate of prediction success [%]"
plot \\
EOF
for name in $nameList; do
  cat <<EOF
  "< grep \"${name}\" out.plot" using 1:3 title "${name}" with lp, \\
EOF
done
cat <<EOF
0 notitle

set terminal png font arial 11 size 1024,768
set output '${pngFileName}'
replot

unset output
set terminal x11
set yrange [*:*]
EOF
}

doPlotMemoryUsage()
{
local pngFileName=$1
local nameList="$2"

cat <<EOF
set yrange [100:]
set logscale y
set key top left
set xlabel "Number of input charactors"
set ylabel "Memory usage [items]"
plot \\
EOF
for name in $nameList; do
  cat <<EOF
  "< grep \"${name}\" out.plot" using 1:4 title "${name}" with lp, \\
EOF
done
cat <<EOF
1 notitle

set terminal png font arial 11 size 1024,768
set output '${pngFileName}'
replot

unset logscale y
unset output
set terminal x11
set yrange [*:*]
EOF
}

nameList1="\
NGram(1) \
NGram(2) \
NGram(3) \
NGram(4) \
NGram(5) \
"

nameList2="\
Brain(1) \
Brain(2) \
Brain(3) \
Brain(4) \
Brain(5) \
"
nameList3="\
SignalPredictor(1) \
SignalPredictor(2) \
SignalPredictor(3) \
SignalPredictor(4) \
SignalPredictor(5) \
"

nameList4="\
NGram(2) \
NGram(3) \
NGram(4) \
Brain(3) \
Brain(4) \
SignalPredictor(3) \
SignalPredictor(4) \
"

#doPlotAccuracy ngram_accuracy.png "$nameList1"
#doPlotAccuracy brain_accuracy.png "$nameList2"
#doPlotAccuracy spd_accuracy.png "$nameList3"
#doPlotAccuracy all_accuracy.png "$nameList4"

doPlotMemoryUsage ngram_mem.png "$nameList1"
doPlotMemoryUsage brain_mem.png "$nameList2"
doPlotMemoryUsage spd_mem.png "$nameList3"
doPlotMemoryUsage all_mem.png "$nameList4"
