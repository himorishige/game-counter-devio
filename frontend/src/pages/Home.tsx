import React from 'react';
import { useGetLogDataByNameQuery } from '../services/game-counter';
import moment from 'moment';
import { LogQueryParams } from '../types';
import { Box, Heading, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';

const Home: React.VFC = () => {
  // 1週間前の日付を取得
  const lastWeek = moment().add(-7, 'days').format('YYYY-MM-DD');

  // Lucy用のデータを取得
  const params: LogQueryParams = {
    username: 'Lucy',
    date: lastWeek,
  };
  const { data, isLoading } = useGetLogDataByNameQuery(params, {});

  // Mike用のデータを取得
  const params2: LogQueryParams = {
    username: 'Mike',
    date: lastWeek,
  };
  const { data: data2, isLoading: isLoading2 } = useGetLogDataByNameQuery(params2, {});

  if (isLoading || isLoading2) return <Box p={4}>Loading...</Box>;
  if (!data || !data2) return <Box p={4}>Missing data!</Box>;

  return (
    <Box p={4}>
      <Box>
        <Heading size="md" mb={4}>
          Lucy
        </Heading>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Date</Th>
              <Th>TotalTime</Th>
            </Tr>
          </Thead>
          <Tbody>
            {data.map((item, index) => (
              <Tr key={index}>
                <Td>{item.date}</Td>
                <Td>{item.totaltime}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
      <Box mt={4}>
        <Heading size="md" mb={4}>
          Mike
        </Heading>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Date</Th>
              <Th>TotalTime</Th>
            </Tr>
          </Thead>
          <Tbody>
            {data2.map((item, index) => (
              <Tr key={index}>
                <Td>{item.date}</Td>
                <Td>{item.totaltime}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
};

export default Home;
