import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { GameCounterItem, GameCounterLogItem, GetQueryParams, LogQueryParams } from '../types';

// .env.localファイルからAPI URLとAPI KEYを取得
const API_URL = process.env.REACT_APP_API_URL!;
const API_KEY = process.env.REACT_APP_API_KEY!;

// RTK Queryを利用したAPIを作成
export const gameCounterApi = createApi({
  reducerPath: 'gameCounterApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
    // headerにAPI KEYを付与
    prepareHeaders: (headers) => {
      headers.set('x-api-key', API_KEY);
      return headers;
    },
  }),
  endpoints: (builder) => ({
    // ユーザー詳細画面でユーザーごとの情報を取得するためのクエリー
    // ユーザ名と期間（UNIXTIME）を送る
    getCounterByName: builder.query<GameCounterItem[], GetQueryParams>({
      query: (params) =>
        `?username=${params.username}&starttime=${params.startTime}&endtime=${params.endTime}`,
    }),
    // ホーム画面でユーザーごとの統計情報を取得するためのクエリー
    // ユーザ名と取得日（YYYY-MM-DD）を送る
    getLogDataByName: builder.query<GameCounterLogItem[], LogQueryParams>({
      query: (params) => `log?username=${params.username}&date=${params.date}`,
    }),
  }),
});

// RTK Queryが自動的に用意してくれる！カスタムフックをエクスポート
export const { useGetCounterByNameQuery, useGetLogDataByNameQuery } = gameCounterApi;
