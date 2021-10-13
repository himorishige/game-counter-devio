import React from 'react';
import { useGetCounterByNameQuery } from '../services/game-counter';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  TableCaption,
  Select,
} from '@chakra-ui/react';
import moment from 'moment';
import { GameCounterItem, GetQueryParams } from '../types';
import { useLocation, useHistory } from 'react-router-dom';

type Props = {
  match: {
    params: {
      username: string;
    };
  };
};

const UserPage: React.VFC<Props> = (props) => {
  const search = useLocation().search;
  const query = new URLSearchParams(search);

  const history = useHistory();

  // 今日の0時0分0秒をunixtime（秒）で取得
  let today = moment(new Date().setHours(0, 0, 0, 0)).unix();

  // パラメータとして日付を受けた場合はその日付をunixtime（秒）へ変換
  if (query.get('date')) {
    today = moment(`${query.get('date')}T00:00:00`).unix();
  }

  // 翌日の0時0分0秒を生成
  const nextDay = today + 86400;

  // 現在時刻を生成
  const now = moment().format('YYYY-MM-DDTHH:mm:ss');

  // ユーザーのログデータを取得
  const params: GetQueryParams = {
    username: props.match.params.username,
    startTime: today,
    endTime: nextDay,
  };
  const { data, isLoading, isFetching } = useGetCounterByNameQuery(params, {
    // 30000秒ごとに自動更新
    pollingInterval: 30000,
  });

  // セレクトボックスで日付を変更した際に日付に合わせたパラメーターを生成してページ更新
  const changeHandler = (value: string) => {
    history.push(`/data/${props.match.params.username}?date=${value}`);
  };

  // ミリ秒を00:00:00のフォーマットに変換する
  const computeDuration = (ms: number) => {
    let target = ms * 1000;
    const h = String(Math.floor(target / 3600000) + 100).substring(1);
    const m = String(Math.floor((target - Number(h) * 3600000) / 60000) + 100).substring(1);
    const s = String(
      Math.round((target - Number(h) * 3600000 - Number(m) * 60000) / 1000) + 100,
    ).substring(1);
    return h + ':' + m + ':' + s;
  };

  // start | end をそれぞれ開始、終了の文字に変換
  const timingCharacter = (str: string) => {
    if (str === 'start') {
      return '開始';
    }
    if (str === 'end') {
      return '終了';
    }

    return '未設定';
  };

  if (isLoading) return <Box p={4}>Loading...</Box>;
  if (!data) return <Box p={4}>Missing data!</Box>;

  // ログを合計して当日の合計時間を計算する
  const totalTime = (logData: GameCounterItem[]) => {
    return computeDuration(
      logData
        .map((item, index, org) => {
          if (org[index + 1]?.flag === 'end') {
            return org[index + 1].timestamp - item.timestamp;
          }
          return 0;
        })
        .reduce((acc, value) => acc + value, 0),
    );
  };

  return (
    <Box p={4} minHeight="320px">
      <Box pb={4}>
        <Select name="date" onChange={(event) => changeHandler(event.target.value)}>
          <option>select date</option>
          {/* 1週間分のセレクトボックスを生成 */}
          {[...Array(6)].map((_, i) => (
            <option key={i} value={moment().add(`-${i}`, 'days').format('YYYY-MM-DD')}>
              {moment().add(`-${i}`, 'days').format('YYYY-MM-DD')}
            </option>
          ))}
        </Select>
      </Box>
      <Heading mb={4}>
        合計時間：
        {totalTime(data)}
      </Heading>
      {isFetching && (
        <Box alignItems="center" justifyContent="center" textAlign="center">
          <Spinner thickness="4px" speed="0.65s" emptyColor="gray.200" color="blue.500" size="xl" />
        </Box>
      )}
      <Table variant="simple" size="sm">
        <TableCaption>更新日時：{now}</TableCaption>
        <Thead>
          <Tr>
            <Th>ID</Th>
            <Th>UserId</Th>
            <Th>Timestamp</Th>
            <Th></Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item, index, data) => (
            <React.Fragment key={item.uid}>
              <Tr>
                <Td>{index + 1}</Td>
                <Td>{item.username}</Td>
                <Td>{moment.unix(item.timestamp).format('YYYY-MM-DD HH:mm:ss')}</Td>
                <Td>{timingCharacter(item.flag)}</Td>
              </Tr>
              {data[index + 1]?.flag === 'end' && (
                <Tr>
                  <Td colSpan={4}>
                    経過時間 {computeDuration(data[index + 1].timestamp - item.timestamp)}
                  </Td>
                </Tr>
              )}
            </React.Fragment>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default UserPage;
