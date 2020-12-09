import requests, os
from threading import Event, Thread

lastStats = {}
monthsIndexToTR = {'01': 'OCAK', '02': 'ŞUBAT', '03': 'MART', '04': 'NİSAN', '05': 'MAYIS', '06': 'HAZİRAN',
                   '07': 'TEMMUZ', '08': 'AĞUSTOS', '09': 'EYLÜL', '10': 'EKİM', '11': 'KASIM', '12': 'ARALIK'}
keysENtoTR = {'date': 'SON GÜNCELLENME TARİHİ',
              'daily': {'case': 'BUGÜNKÜ VAKA SAYISI', 'death': 'BUGÜNKÜ VEFAT SAYISI',
                        'recovered': 'BUGÜNKÜ İYİLEŞEN SAYISI', 'test': 'BUGÜNKÜ TEST SAYISI',
                        'patient': 'BUGÜNKÜ HASTA SAYISI'},
              'total': {'patient': 'TOPLAM HASTA SAYISI', 'death': 'TOPLAM VEFAT SAYISI',
                        'icuPatient': 'TOPLAM YOĞUN BAKIM HASTA SAYISI',
                        'intubatedPatient': 'TOPLAM ENTUBE HASTA SAYISI', 'recovered': 'TOPLAM İYİLEŞEN HASTA SAYISI',
                        'seriouslyIllPatient': 'AĞIR HASTA SAYISI', 'test': 'TOPLAM TEST SAYISI'},
              'weekly': {'pneumoniaRate': 'BU HAFTAKİ HASTALARDA ZATÜRRE ORANI (%)',
                         'hospitalBedOccupancyRate': 'BU HAFTAKİ YATAK DOLULUK ORANI (%)',
                         'adultIcuOccupancyRate': 'BU HAFTAKİ ERİŞKİN YOĞUN BAKIM DOLULUK ORANI (%)',
                         'ventilatorOccupancyRate': 'BU HAFTAKİ VENTİLATÖR DOLULUK ORANI (%)',
                         'averageFiliationTime': 'BU HAFTAKİ ORTALAMA FİLYASYON SÜRESİ (saat)',
                         'averagePositiveContactDetectionTime': 'BU HAFTAKİ ORTALAMA TEMASLI TESPİT SÜRESİ (saat)',
                         'filiationRate': 'BU HAFTAKİ FİLYASYON ORANI (%)'}}
checkInterval = 1 * 60 # seconds
apiURL = os.getenv('COVIDAPI_URL', 'http://localhost:5000')
apiEndpoint = '/today-all'
telegramAPIToken = os.getenv('TELEGRAM_API_TOKEN', '')
telegramChatID = os.getenv('TELEGRAM_CHAT_ID', '')


class TimerThread(Thread):
    def __init__(self, event, interval, func, *args, **kwargs):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        while not self.stopped.wait(self.interval):
            self.func(*self.args, **self.kwargs)


def getStats(dataURL, dataEndpoint):
    try:
        response = requests.get(dataURL + dataEndpoint)
        stats = response.json()

        return stats
    except Exception as e:
        print('>>>[ERROR] Cannot get data!', e)
        return None


def sendTelegram(stats, apiToken, chatID):
    if (apiToken != '') and (chatID != ''):
        date = stats.pop('date')
        text = f'{keysENtoTR["date"]}: *{date}*\n'
        for statType, statDict in stats.items():
            text += '\n'
            for statKey, statValue in statDict.items():
                if statValue is not None:
                    text += f'_{keysENtoTR[statType][statKey]}:_ '
                    text += f'*{statValue}*\n'
        text = text.replace('.', '\\.').replace('-', '\\-').replace('%', '\\%').replace('(', '\\(').replace(')', '\\)')

        headers = {'Content-Type': 'application/json'}
        payload = {'chat_id': chatID, 'parse_mode': 'MarkdownV2', 'text': text}
        telegramURL = telegramURL = 'https://api.telegram.org/' + apiToken + '/sendMessage'
        try:
            response = requests.post(telegramURL, headers=headers, json=payload)
            print('Message status code:', response.status_code)
        except Exception as e:
            print('>>>[ERROR] Cannot send message !', e)
            return
    else:
        return


def routine():
    global lastStats

    try:
        stats = getStats(apiURL, apiEndpoint)
        if (stats is not None) and (stats != lastStats):
            lastStats = dict(stats)
            sendTelegram(dict(lastStats), telegramAPIToken, telegramChatID)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    routine()
    stopFlag = Event()
    thread = TimerThread(stopFlag, checkInterval, routine)
    thread.start()
