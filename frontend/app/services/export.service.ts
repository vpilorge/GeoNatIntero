import { Injectable } from "@angular/core";
import {
  HttpClient,
  HttpEvent,
  HttpHeaders,
  HttpRequest,
  HttpEventType,
  HttpErrorResponse
} from "@angular/common/http";
import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { share } from 'rxjs/operators/share';
import { interval } from 'rxjs/observable/interval';
// import 'rxjs/Rx';  // Observer.interval

import { AppConfig } from "@geonature_config/app.config";

// interface Export {
//   path: string;
//   date: Date;
// }
export class Export {
  constructor(public path: string, public date: Date) {}
}

const apiEndpoint='http://localhost:8000/interop';

@Injectable()
export class ExportService {
  private store: { exports: Export[] }
  private _exports: BehaviorSubject<Export[]>

  constructor(private _api: HttpClient) {
    this.store = { exports: new Array<Export>() }
    this._exports = <BehaviorSubject<Export[]>>new BehaviorSubject([]);
  }

  get exports() {
    return this._exports.asObservable().pipe(share())
  }

  getExports() {
    /*let exportList = */
    this._api.get(`${apiEndpoint}/exports`).subscribe(
      (exports: Export[]) => {
        this.store.exports = exports.map(x => new Export(x[0], x[1]));
        this._exports.next((<any>Object).assign({}, this.store).exports);
        console.debug(`getExports(): ${this.store.exports.length} exports.`)
      },
      error => console.error(error),
      () => {
        // exportList.unsubscribe()
      }
    )
  }

  downloadExport(submissionID: number) {
    const url = `${apiEndpoint}/exports/export_${submissionID}.csv`
    window.open(url)
    /*
    const request = new HttpRequest('GET', url, {reportProgresss: true, responseType: 'text'});
    this._api.request(request).subscribe(
      event => {
        console.debug('start', event.type)
        if (event.type === HttpEventType.DownloadProgress) {
          console.debug('dload', event)
            let kbLoaded = Math.round(event.loaded / 1024);
            // const percentage = 100 / event.total * event.loaded;
            console.log(`Downloading ${kbLoaded}Kb.`);
        }
        if (event.type === HttpEventType.Response) {
          console.log(event.body);
        }
      },
      (err: HttpErrorResponse) => {
        console.log(err.error);
        console.log(err.name);
        console.log(err.message);
        console.log(err.status);
      }
    );
    */
  }

  getExportProgress(submissionID: number) {
    let progress = Observable.interval(1500)
      .switchMap(() => this._api.get(`${apiEndpoint}/progress/${submissionID}`))
      .map(data => data.json())
      .takeWhile(data => data.status === '-2')
      .subscribe(
        data => {
          // https://www.postgresql.org/message-id/CADdR5ny_0dFwnD%2BsuBnV1Vz6NDKbFHeWoV1EDv9buhDCtc3aAA%40mail.gmail.com
          // then update progressbar
          console.debug(data)
        },
        error => console.error(error),
        () => {
          progress.unsubscribe();
          window.location.href = `${apiEndpoint}/exports/export_${submissionID}.csv`;
        });
  }
}
