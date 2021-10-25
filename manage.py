import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--testmode/--live', default=False)
def start(testmode):
    if testmode:
        click.echo('*** WARNING: Running in testmode.')
        click.echo('- longpolling mode. Testing TOKEN in use.')
        import ifaxbotcovid.bot.bot_testmode
        ifaxbotcovid.bot.bot_testmode.run_long_polling()
    else:
        click.echo('*** INFO: Running in livemode.')
        pass


if __name__ == '__main__':
    cli()
