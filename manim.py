#!/usr/bin/env python
import manimlib.config
import manimlib.extract_scene
# import manimlib.stream_starter

if __name__ == "__main__":
    args = manimlib.config.parse_cli()
    config = manimlib.config.get_configuration(args)
    manimlib.extract_scene.main(config)
