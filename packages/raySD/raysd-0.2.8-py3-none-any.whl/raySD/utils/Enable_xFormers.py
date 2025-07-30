def enable_xformers_if_available(pipe):
    try:
        import xformers
        pipe.enable_xformers_memory_efficient_attention()
        print("xformers is available and has been enabled.")
    except ImportError:
        print("xformers is NOT installed. Running without xformers.")
    except Exception as e:
        print(f"xformers is installed but could not be enabled: {e}")
