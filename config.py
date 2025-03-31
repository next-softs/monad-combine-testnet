
class GeneralSettings:
    # использовать прокси | True - вкл / False - откл
    useProxies = True

    # кол-во потоков
    threads = 10

    # сколько одновременно запускать аккаунтов
    start_accs = 3

    # макс. кол-во символов в дробной части объёмов [от, до]
    precision = [4, 8]

    # задержки между стартом аккаунтов
    delay_start = [60, 600]

class GasZipSettings:
    # сколько тратим ETH на покупку MON [от, до]
    amounts = [0.0001, 0.00015]

    # сети которые можем использовать для покупки MON ["op", "arb", "base", "unichan"]
    chains = ["op", "arb", "base"]

    # если баланс в MON < указанного, то бриджим
    max_amount = 0.001

    # сколько бриджим ETH для накрутки транзакций [от, до]
    amounts_transactions = [0.00065, 0.00075]

    # сети которые можем использовать для покупки MON ["op", "arb", "base", "unichan"]
    chains_transactions = ["op", "unichan"]

    # задержки между бриджами
    delay_transactions = [10, 20]

    # сколько на кошельке должно быть транзакций
    count_transactions = 11

    # бриджить в одну и туже сеть, если True бот может отправить транзакцию из base в base
    use_same_chain = False

class SepoliaToMonSettings:
    # сколько тратим на MON [от, до] | минимальный объём 0.02
    amounts = [0.98, 1.1]

    # если баланс в MON < указанного, то бриджим
    max_amount = 1.001

    # если в монаде есть ETH, то не бриджим из сеполии, а сразу свапаем на MON
    use_eth_monad = True

class SwapHouseSettings:
    # сколько тратим MON на токен [от, до]
    amounts = [0.0001, 0.002]

    # монеты на которые свапаем ["CHOG", "YAKI", "DAK"]
    coins = ["CHOG", "YAKI", "DAK"]

    # задержка между свапами [от, до]
    delay = [5, 60]

class MintNftSettings:
    # макс. стоимость NFT в MON
    max_amount = 0.05

    # Минтим NFT только если её нет на кошельке True/False
    mint_different = True

    # адреса нфт magiceden, [address, price] ставим 0, если FREE MINT
    # тестировал только на оф. коллекциях, на других может не работать
    address_magiceden_nft = [
        ["0xfd3b54bd826cea09d15e87f95a869ecf3e462f92", 0.005],
        ["0x8f9571324a98d4c78b6530c97487d34607cdf244", 0.01],
        ["0xb2ea0ff3ad4134367fb7dc75d48b3493e5a09c81", 0],
        ["0x9e313cbd57a35661072c1b96684454cebd09acdc", 0],
        ["0x913bf9751fe18762b0fd6771edd512c7137e42bb", 0],
        ["0x690cfacdc08dc7da79736906cd506890d6ca224a", 0],
        ["0x65626148cfab93d88f669bec505c457fb8ff51db", 0],
        ["0xf9c6fcd5c8ef350df31b39e9e7308d521add1a94", 0],
        ["0xa8800432385590f5143d46d9bd29389a759705ac", 0],
        ["0x63300257926af6f2a1bf2d4efb4240d8d8f250d6", 0]
    ]


    # Задержка между минтом на одном кошельке
    delay = [5, 60]

class SwapsSettings:
    # какими дексами пользуемся во время свапов ["Uniswap", "BeanExchange", "Monorail", "OctoExchange"]
    exchanges = ["BeanExchange", "Monorail", "OctoExchange"]

    # объём MON который тратим на покупку монет [от, до]
    amounts = [0.01, 0.1]

    # монеты которые используем при свапах ["MON", "USDC", "USDT", "ETH", "WETH", "WBTC", "DAK", "MUK", "CHOG", "YAKI"]
    coins = ["MON", "USDC", "DAK", "MUK", "CHOG", "YAKI"]

    # начинаем принудительно продавать монеты, если баланс MON меньше заданного
    min_balance_mon = 0.3

    # сколько свапов делаем за раз [от, до]
    repeat_count = [0, 4]

    # вероятность продать следующим трейдом после покупки, 0 - не продавать сразу / 100 - всегда сразу продавать
    auto_sell = 50

    # задержка между свапами внутри сессии
    delay_swap = [15, 60]

    # задержка между сессиями
    delay_sessions = [600, 3600]

class StakeSettings:
    # какие используем сервисы для стейкинга ["apriori", "kintsu", "magma", "shmonad"]
    protocols = ["apriori", "kintsu", "magma", "shmonad"]

    # сколько должно быть застейкано (если уже застейкано 1MON, но выпадает 0.6, то 0.4 будет выведено) [от, до]
    amounts = [0.1, 0.3]

    # вероятность того, что выведем все MON из стейкинга
    # 10 - значит с 10% шансом все выводим, 0 - не выводить, 100 - выводить всегда если баланс больше 0
    withdraw = 90

    # кол-во действий за сессию
    repeat_count = [0, 3]

    # задержка между повторениями
    delay = [15, 60]

class RandomSettings:
    # вероятности модулей, если ставим 0, то этот модуль не будет работать | 0.1 - 10%, 1 - 100%
    actions = {
        "swap": 0.4,
        "stake": 0.4,
        "deploy": 0.1,
        "swap_house": 0.05,
    }

    # кол-во действий за сессию [от, до]
    repeat_count = [1, 3]

    # задержка между повторениями внутри сессии [от, до]
    delay_actions = [60, 600]

    # задержка между сессиями [от, до]
    delay_sessions = [600, 3600]

    # использовать кран ["gas.zip"]
    faucets = ["gas.zip"]

    # включить/отключить работу monad.pizza True/False
    monad_pizza = True

class SuperboardSettings:
    # выполнять квесты только monad
    monad_only = False

    # задержка между выполнением заданий [от, до]
    delay_task = [5, 15]

    # задержка между выполнением квестов [от, до]
    delay_quest = [10, 30]

class MonadPizzaSettings:
    # рефереры выбирается случайный, если поставить [], то аккаунт не будет рефералом
    referrer_address = ["0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000"]

    # сколько делаем кликов перед запуском автокликера [от, до]
    clicks = [0, 2]

    # доп. задержка между кликами [от, до]
    delay_clicks = [2, 15]

    # покупать пропуски True/False
    buy_battle_pass = True

    # задержки между клеймами пропусков [от, до]
    delay_battle_pass = [5, 30]

    # автоматически клеймить доступны бейджи True/False
    badges_claim = True

    # задержки между клеймами бейджей [от, до]
    delay_badges = [5, 30]






