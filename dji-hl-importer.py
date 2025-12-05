#!/usr/bin/env python

import subprocess

resolve = app.GetResolve()
pm = resolve.GetProjectManager()

project = pm.GetCurrentProject()

media_pool = project.GetMediaPool()


def main():
    for clip in media_pool.GetRootFolder().GetClipList():
        type = str(clip.GetClipProperty("Type"))
        if "Video" not in type:
            continue
        # Relevant attributes
        # Clip Name
        # File Path
        name = clip.GetClipProperty("Clip Name")

        # Check only for DJI clips
        if not name.startswith("DJI_"):
            continue

        path = clip.GetClipProperty("File Path")
        fps = clip.GetClipProperty("FPS")
        print(f"Clip Name: {name}")
        print(f"File Path: {path}")
        print(f"Framerate: {fps}")

        highlights = get_clip_highlights(path)

        for hl in highlights:
            hl_tc = float(hl)
            hl_frame_id = get_frame_id_from_tc(hl_tc, float(fps))

            # Check if Marker already exists at this frame
            existing_markers = clip.GetMarkers()
            if existing_markers:
                if existing_markers.get(hl_frame_id):
                    print(
                        f"Marker already exists at frame {hl_frame_id} (tc: {hl_tc}s). Skipping..."
                    )
                    continue

            success = clip.AddMarker(
                hl_frame_id, "Yellow", f"Highlight @ {hl_tc}s", "", 1.0
            )
            print(
                f"Added Highlight Marker at frame {hl_frame_id} (tc: {hl_tc}s)"
            ) if success else print(
                f"Failed to add Marker at frame {hl_frame_id} (tc: {hl_tc}s)"
            )

        print("")


def get_clip_highlights(file_path: str) -> []:
    # exiftool -G1 -s -Highlight\\* -ee
    result = subprocess.run(
        ["exiftool", "-G1", "-s", "-Highlight*", "-ee", file_path],
        capture_output=True,
        text=True,
    )
    # Format Text Output of exiftool which is something like "[QuickTime]     HighlightMarkers                : 3.649, 6.675"
    text_result = result.stdout.split(":")[1].strip()

    return [hl_tc.strip() for hl_tc in text_result.split(",")]


def get_frame_id_from_tc(tc: float, fps: float) -> int:
    return round(tc * fps)


if __name__ == "__main__":
    main()
