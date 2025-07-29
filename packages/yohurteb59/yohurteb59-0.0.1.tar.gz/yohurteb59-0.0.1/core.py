def ft_tqdm(lst: range) -> None:
    """
    Make a loading bar for more visual

    Args:
        lst (range): the range wich be travaled

    Returns:
        None: This function does not return a value.
    """
    try:
        for i, elem in enumerate(lst):
            progr = int(i) + 1
            total = int(len(lst))
            percent = int((progr / total) * 100)
            bar_length = 98
            progr_length = int(bar_length * progr // total)

            bar = "█" * progr_length
            bar = bar.ljust(bar_length, "=")

            print(f"\r{percent}%|{bar}| {progr}/{total}", end="", flush=True)
            yield elem
    except Exception as err:
        print("Error ->", err)


if __name__ == "__main__":
    ft_tqdm()
