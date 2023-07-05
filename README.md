This repository contains scores, various project files and other source
material for [my music][sc]. Most of them are licensed under a Creative Commons
Attribution-ShareAlike 3.0 Unported License.

You should have received a copy of the license along with this
work. If not, see [CC-BY-SA 3.0][ccbysa30]

  [sc]: https://soundcloud.com/athoshun
  [ccbysa30]: http://creativecommons.org/licenses/by-sa/3.0/

Gear and Setup
--------------
 * Notation: [MuseScore][musescore]
 * Guitar Effects, Amp Simulation (signal chain):
    * Guitar: [Dean Vendetta XM][vendettaxm]
       * Tuning: E-standard, D-standard
       * Strings: [D'Addario EXL115][exl115]
    * [BOSS NS-2][ns2]:
       * Threshold: 10 o'clock
       * Decay: min
       * Mode: mute
    * [BOSS BD-2][bd2]:
       * Level: 10:30 o'clock
       * Tone: max
       * Gain: 10:30 o'clock
    * [BOSS OS-2][os2]:
       * Level: 1 o'clock
       * Tone: 2 o'clock
       * Drive: 11 o'clock
       * Color: 2:30 o'clock
    * [KORG AX5G][ax5g] (frequently used settings):
       * Expression Pedal Assignment: Volume (min: 5.3, max: 10.0)
       * Program 1:
          * PreFX: off
          * Drive/Amp: A1 (Black 2x12)
             * Gain: 5.3
             * P1 (Treble): 5.7
             * P2 (Middle): 9.0
             * P3 (Bass): 5.3
             * P4 (Volume): 9.0
             * P5 (Amp/Line): A1 (connected to a clean sounding amp)
          * Level/NR/Cab:
             * Level: 5.0
             * Noise Reduction Sensitivity: 7.7
             * Cabinet Model: C6 (AC30TBX)
          * Mod: off
          * Delay/Reverb: off
       * Program 2:
          * PreFX: off
          * Drive/Amp: A1 (Black 2x12)
             * Gain: 5.0
             * P1 (Treble): 6.3
             * P2 (Middle): 9.0
             * P3 (Bass): 8.0
             * P4 (Volume): 9.0
             * P5 (Amp/Line): A1 (connected to a clean sounding amp)
          * Level/NR/Cab:
             * Level: 5.0
             * Noise Reduction Sensitivity: 7.7
             * Cabinet Model: C8 (UK T75)
          * Mod: off
          * Delay/Reverb: off
       * Program 3 and 4: like Program 1 and 2, but
          * Delay/Reverb: F3 (Stereo Delay)
             * Mix: 2.7
             * P1 (Time): 3.3
             * P2 (Feedback): 7.0
             * P3 (Tone): 5.3
       * Program 5:
          * PreFX: off
          * Drive/Amp: A0 (Boutique Clean)
             * Gain: 5.0
             * P1 (Treble): 6.3
             * P2 (Middle): 8.0
             * P3 (Bass): 7.7
             * P4 (Volume): 9.7
             * P5 (Amp/Line): A1 (connected to a clean sounding amp)
          * Level/NR/Cab:
             * Level: 10.0
             * Noise Reduction Sensitivity: 7.7
             * Cabinet Model: C9 (US V30)
          * Mod: off
          * Delay/Reverb: off
       * Program 6:
          * PreFX: off
          * Drive/Amp: A0 (Boutique Clean)
             * Gain: 5.0
             * P1 (Treble): 6.3
             * P2 (Middle): 8.0
             * P3 (Bass): 7.7
             * P4 (Volume): 9.7
             * P5 (Amp/Line): A1 (connected to a clean sounding amp)
          * Level/NR/Cab:
             * Level: 10.0
             * Noise Reduction Sensitivity: 7.7
             * Cabinet Model: C6 (AC30TBX)
          * Mod: off
          * Delay/Reverb: off
       * Program 7 and 8: like Program 5 and 6, but
          * Delay/Reverb: F3 (Stereo Delay)
             * Mix: 2.7
             * P1 (Time): 3.3
             * P2 (Feedback): 7.0
             * P3 (Tone): 5.3
       * Program 9 and 10: like Program 3 and 4, but
          * PreFX: F6 (Chorus/Flanger)
             * Speed: 3.7
             * P1 (Depth): 2.3
             * P2 (Reso): 0.0
             * P3 (Manual): 7.3
       * Program 11: like Program 1, but
          * PreFX: F8 (Ring Modulator)
             * Osc Freq: 7.0
             * P1 (Effect): 8.0
             * P2 (Direct): 10.0
             * P3 (Filter): 5.0
          * Mod: F0 (Classic Chorus)
             * Speed: 9.0
             * P1 (Depth): 10.0
             * P2 (Manual): 8.0
             * P3 (Mode): 1
          * Delay/Reverb: F9 (Hall)
             * Mix: 3.3
             * P1 (Time): 6.0
             * P2 (Hi Damp): 2.0
             * P3 (Lo Damp): 2.0
       * Program 12: like Program 2, but
          * PreFX: F6 (Chorus/Flanger)
             * Speed: 3.7
             * P1 (Depth): 2.3
             * P2 (Reso): 2.0
             * P3 (Manual): 7.3
          * Mod: F4 (Duo Phaser)
             * Speed 1: 3.3
             * P1 (Speed 2): 5.0
             * P2 (Depth): 6.3
             * P3 (Reso): 2.3
             * P4 (Mode): 5
          * Delay/Reverb: F6 (Spring)
             * Mix: 4.0
             * P1 (Time): 5.0
             * P2 (Hi Damp): 3.0
             * P3 (Lo Damp): 4.0
       * Program 13 and 14: like Program 3 and 4, but
          * PreFX: F3 (Slow Attack)
             * Attack: 10.0
          * Delay/Reverb: F3 (Stereo Delay)
             * Mix: 3.3
       * Program 15:
          * PreFX: F2 (Acoustic simulator)
             * Top: 10.0
             * P1 (Body): 8.3
             * P2 (Type): 3
             * P3 (Mix): 7.0
          * Drive/Amp: off
          * Level/NR/Cab:
             * Level: 5.0
             * Noise Reduction Sensitivity: 7.7
          * Mod: off
          * Delay/Reverb: off
       * Program 16 like Program 2, but:
          * PreFX: F5 (U-Vibe/Phaser)
            * Speed: 7.0
            * P1 (Depth): 5.0
            * P2 (Order): Pr
            * P3 (Type): U2
            * P4 (Manual): 1.0
          * Mod: F8 (Random Step Filter)
             * Speed: 7.3
             * P1 (Mix): 8.0
             * P2 (Resonance): 8.0
             * P3 (Manual): 8.0
             * P4 (Depth): 8.7
          * Delay/Reverb: F3 (Stereo Delay)
             * Mix: 10.0
             * P1 (Time): 9.0
             * P2 (Feedback): 9.7
             * P3 (Tone): 8.7
          * Expression Pedal Assignment: FX Param (min: 0.0, max: 10.0)
       * Program 17 like Program 16, but:
          * Mod: F8 (Random Step Filter)
             * Speed: 7.3
             * P1 (Mix): 8.0
             * P2 (Resonance): 7.0
             * P3 (Manual): 8.0
             * P4 (Depth): 9.0
          * Delay/Reverb: F3 (Stereo Delay)
             * Mix: 8.0
             * P1 (Time): 9.0
             * P2 (Feedback): 9.0
             * P3 (Tone): 6.0
          * Expression Pedal Assignment: FX Param (min: 0.0, max: 10.0)
       * Program 18:
          * PreFX: F3 (Slow Attack)
             * Attack: 10.0
          * Drive/Amp: A5 (UK 80)
             * Gain: 10.0
             * P1 (Treble): 7.0
             * P2 (Middle): 9.3
             * P3 (Bass): 5.0
             * P4 (Volume): 6.0
             * P5 (Amp/Line): A3 (connected to a stack, 4x12 closed-back cab.)
          * Level/NR/Cab:
             * Level: 5.0
             * Noise Reduction Sensitivity: 7.7
             * Cabinet Model: C8 (UK T75)
          * Mod: F2 (Classic Flanger)
             * Speed: 1.7
             * P1 (Resonance): 6.0
             * P2 (Depth): 7.0
             * P3 (Manual): 5.0
             * P4 (Mix): 6.0
          * Delay/Reverb: F6 (Spring)
             * Mix: 7.0
             * P1 (Time): 6.3
             * P2 (Hi Damp): 5.0
             * P3 (Lo Damp): 4.0
    * Input: [Behringer UCG102][ucg102]
 * MIDI:
    * [Alesis Q49][q49]
    * [Arturia Keystep 37][ks37]
    * [M-Audio SP 2][sp2]
 * Drums, Synths, Samplers, Sequencers, etc.: [LMMS][lmms]
 * Piano: [mda Piano][mdapiano]
 * Synth:
    * [JS80P][js80p]
    * [ZynAddSubFX][zynaddsubfx]
 * Singing Synth: [Vocaloid][vocaloid], [Yukari Lin][yukarilin]
 * DAW: [Reaper][reaper]

  [musescore]: https://musescore.org/
  [vendettaxm]: http://www.deanguitars.com/query?upc=819998136710
  [exl115]: http://www.daddario.com/DADProductDetail.Page?ActiveID=3769&ProductID=23
  [ns2]: https://www.boss.info/us/products/ns-2/
  [bd2]: https://www.boss.info/us/products/bd-2/
  [os2]: https://www.boss.info/us/products/os-2/
  [ax5g]: http://www.korg.com/us/support/download/manual/1/35/1748/
  [q49]: http://www.alesis.com/products/legacy/q49
  [ks37]: https://www.arturia.com/products/hybrid-synths/keystep-37/overview
  [sp2]: https://m-audio.com/products/view/sp-2
  [ucg102]: http://www.musictri.be/Categories/Behringer/Computer-Audio/Interfaces/UCG102/p/P0198
  [lmms]: https://lmms.io/
  [mdapiano]: http://mda.smartelectronix.com/synths.htm
  [js80p]: https://attilammagyar.github.io/js80p/
  [zynaddsubfx]: http://zynaddsubfx.sourceforge.net/
  [vocaloid]: https://www.vocaloid.com/en/
  [yukarilin]: https://www.vocaloid.com/en/articles/yuzukiyukari
  [reaper]: https://www.reaper.fm/
