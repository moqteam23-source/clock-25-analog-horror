# Analog-horror character asset pack

10 pose SVGs built from ONE shared rig. Head, torso, arms and legs are the same
primitives in every pose; only joint rotations (and, for the dog, the head type)
change. Palette is black, white, red, yellow only. No gradients, no fur, no 3D.

## Files
- 01_human_standing.svg   (carries the optional yellow #you-marker)
- 02_human_sitting.svg     (on a #stool)
- 03_human_sleeping.svg    (lying on a #bed, eyes closed)
- 04_human_walking.svg
- 05_dog_standing.svg      (upright, red eye)
- 06_dog_sitting.svg
- 07_dog_walking.svg
- 08_dog_lying_bed.svg
- 09_dog_facing.svg        (front head, neutral #mouth)
- 10_dog_smile.svg         (front head, unnatural red grin in #mouth)
- contact_sheet.png        (preview of all 10)

## Palette
black #000000, white #FFFFFF, danger red #F81C28, highlight yellow #F9DE75.

## Rig and animation
Every body part is a named group. Rotatable joints are nested as:

    <g id="arm-L" data-pivot="358,282" transform="translate(358,282)">
      <g id="arm-L-joint" transform="rotate(0)">        <!-- animate THIS rotate -->
        <rect .../>                                     <!-- upper arm -->
        <g id="arm-L-lower" data-pivot="0,135" transform="translate(0,135)">
          <g id="arm-L-lower-joint" transform="rotate(0)"> <rect/> </g>  <!-- forearm/elbow -->
        </g>
      </g>
    </g>

To animate, change the angle on the `*-joint` group (SVG `rotate(DEG)`), or in CSS/JS
rotate that group (its origin is already the pivot, 0 0 in its own frame). `data-pivot`
gives the pivot in page coordinates for reference.

Rotatable handles present in every file:
- head-joint            pivot at the neck
- arm-L-joint / arm-R-joint      shoulders
- arm-L-lower-joint / arm-R-lower-joint   elbows
- leg-L-joint / leg-R-joint      hips
- shin-L / shin-R (their transform rotate)   knees
- tail-joint           (dog only) tail base
- mouth                (dog front head) jaw/mouth; swap neutral line for the grin to animate a smile
- eye / eye-L / eye-R  turn fill to #F81C28 for the "threat" reveal
- snout, ear-L, ear-R, skull, torso, foot-L, foot-R   named for completeness

## Notes
- #bg is a black rectangle for standalone preview; delete it to composite the figure
  on your own background.
- #ground, #bed, #stool are scene props, not part of the character; remove freely.
- viewBox is 0 0 800 1000 in every file so the rig lines up across poses.
