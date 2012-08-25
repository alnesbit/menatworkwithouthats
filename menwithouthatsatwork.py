#!/usr/bin/python2.6
#
# A starry-eyed, future-of-music hack by Andrew Nesbit (The Echo Nest)
# and Matt Ogle (This Is My Jam), 24-25 August, 2012 for Music Hack
# Day Edinburgh.
#
# Some bits of this are based on the example "capsule" by Tristan
# Jehan and Jason Sundram (although I'm not sure how much of that is
# now left).

import sys
from optparse import OptionParser

import echonest.audio as audio
import echonest.modify as modify
from echonest.action import Crossmatch

######################################################################
#
# Set your Echo Nest API key in the environment variable
# ECHO_NEST_API_KEY before you run this program the usual way, so like
# this:
#
# export ECHO_NEST_API_KEY="the key you got from the Echo Nest Developer Site"
#
######################################################################


# Thank you, stackoverflow.com
def interleave(*args):
    for idx in range(0, min(len(arg) for arg in args)):
        for arg in args:
            try:
                yield arg[idx]
            except IndexError:
                continue


def alternate(*args):
    for idx in range(0, min(len(arg) for arg in args)):
        go_to_next_idx = False
        for arg in args:
            if not go_to_next_idx:
                try:
                    yield arg[idx]
                    go_to_next_idx = True
                except IndexError:
                    continue


def choppy_choppy(du, sd, du_beats, sd_beats, droppy=False):
    du_collect = []
    sd_collect = []
    for b in du_beats:
        new = du[b]
        du_collect.append(new)
    for b in sd_beats:
        new = sd[b]
        sd_collect.append(new)
    if not droppy:
        f = interleave
    else:
        f = alternate
    collect = list(f(du_collect, sd_collect))
    return collect


def matchy_matchy(du, sd, du_beats, sd_beats):
    r1 = [(t.start, t.duration) for t in du_beats]
    r2 = [(t.start, t.duration) for t in sd_beats]
    m = min(len(r1), len(r2))
    r1 = r1[:m]
    r2 = r2[:m]
    out = Crossmatch((du, sd), (r1, r2))
    return out.render()


def get_beats_from_section(section):
    beats = []
    for bar in section.children():
        beats.extend(bar.children())
    return beats


def thedownundersafetydance(down_under, safety_dance):
    du_sections = down_under.analysis.sections
    sd_sections = safety_dance.analysis.sections
    
    collect = []
    for n in range(min(len(du_sections), len(sd_sections))):
        du_beats = get_beats_from_section(du_sections[n])
        sd_beats = get_beats_from_section(sd_sections[n])
        process_index = n % 3
        if process_index == 0:
            new = choppy_choppy(down_under, safety_dance, du_beats, sd_beats)
            collect.extend(new)
        elif process_index == 2:
            new = choppy_choppy(down_under, safety_dance, du_beats, sd_beats, droppy=True)
            collect.extend(new)
        else:
            #new = matchy_matchy(down_under, safety_dance, du_beats, sd_beats)
            new = matchy_matchy(safety_dance, down_under, sd_beats, du_beats)
            collect.append(new)

    out = audio.assemble(collect, numChannels=2)
    return out


def main():
    usage = "Usage: %s <path_to_down_under_by_men_at_work.mp3> <path_to_safety_dance_by_men_with_hats.mp3>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
    down_under = audio.LocalAudioFile(args[0])
    safety_dance = audio.LocalAudioFile(args[1])
    out = thedownundersafetydance(down_under, safety_dance)
    out.encode("thesafetydancedownunder.mp3")


if __name__ == '__main__':
    main()
