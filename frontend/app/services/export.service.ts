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
import 'rxjs/add/observable/interval';
import 'rxjs/add/operator/takeWhile';

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
  private _blob: Blob = null

  constructor(private _api: HttpClient) {
    this.store = { exports: new Array<Export>() }
    this._exports = <BehaviorSubject<Export[]>>new BehaviorSubject([]);
  }

  get exports() {
    return this._exports.asObservable().pipe(share())
  }

  getExports() {
    /*let exportList = */
    // this._api.get<Export[]>(`${apiEndpoint}/exports`).subscribe(
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

  downloadExport(submissionID: number, ext='csv') {
    const url = `${apiEndpoint}/exports/export_${submissionID}.${ext}`
    // window.open(url)
    this._api.get(url, {
      headers: new HttpHeaders().set('Content-Type', `text/${ext}`),
      observe: 'events',
      responseType: 'blob',
      reportProgress: true,
    }).subscribe(
      event => {
        if (event.type === HttpEventType.DownloadProgress) {
            let kbLoaded = Math.round(event.loaded / 1024);
            // const percentage = 100 / event.total * event.loaded;
            console.log(`Downloading ${kbLoaded}Kb.`);
        }
        if (event.type === HttpEventType.Response) {
          // this.blob = new Blob([event.body], {type: event.headers.get("Content-Type")});
          this._blob = new Blob([event.body], {type: `text/${ext}`});
        }
      },
      (err: HttpErrorResponse) => {
        console.log(err.error);
        console.log(err.name);
        console.log(err.message);
        console.log(err.status);
      },
      () => {
        let link = document.createElement("a")
        link.href = URL.createObjectURL(this._blob)
        link.setAttribute('visibility','hidden')
        link.download = `${submissionID}.${ext}`
        link.onload = function() { URL.revokeObjectURL(link.href) }
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    );
  }


  getExportProgress(submissionID: number, ext='csv') {
    let progress = Observable.interval(1500)
      .switchMap(() => this._api.get(`${apiEndpoint}/progress/${submissionID}`))
      .map(data => data.json())                   // TODO: export interface ExportProgress {}
      .takeWhile(data => data.status === '-2')
      .subscribe(
        data => {
          // progress feedback:
          // https://www.postgresql.org/message-id/CADdR5ny_0dFwnD%2BsuBnV1Vz6NDKbFHeWoV1EDv9buhDCtc3aAA%40mail.gmail.com
          console.debug(data)
        },
        error => console.error(error),
        () => {
          progress.unsubscribe();
          window.open(`${apiEndpoint}/exports/export_${submissionID}.${data.format}`);
        });
  }
}
