"""main entry for e3smlab command-line interface"""

def main():
    from e3smlab import E3SMlab
    ret, _ = E3SMlab().run_command()
    return ret

if __name__ == "__main__":
    main()
