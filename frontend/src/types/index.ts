// ログ記録用テーブルの型
export type GameCounterItem = {
  uid: string;
  username: string;
  timestamp: number;
  date: string;
  time: string;
  flag: string;
};

// 統計ログ記録用テーブルの型
export type GameCounterLogItem = {
  username: string;
  date: string;
  totaltime: string;
};

// ログ記録用テーブルへのクエリの型
export type GetQueryParams = {
  username: string;
  startTime: number;
  endTime: number;
};

// 統計ログ記録用テーブルへのクエリの型
export type LogQueryParams = {
  username: string;
  date: string;
};
