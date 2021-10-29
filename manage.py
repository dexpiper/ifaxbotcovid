import click


@click.group()
def cli():
    pass


@cli.command()
def runtestmode():
    click.echo('*** WARNING: Running in testmode.')
    click.echo('- longpolling mode. Testing TOKEN in use.')
    import ifaxbotcovid.bot.bot_testmode
    ifaxbotcovid.bot.bot_testmode.run_long_polling()


if __name__ == '__main__':
    cli()
