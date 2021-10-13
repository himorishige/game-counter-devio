import React from 'react';
import { useHistory } from 'react-router-dom';
import { Button, Stack } from '@chakra-ui/react';

const Header: React.VFC = () => {
  const history = useHistory();

  return (
    <Stack direction="row" p={4}>
      <Button colorScheme="teal" onClick={() => history.push('/')}>
        Home
      </Button>
      <Button colorScheme="blue" onClick={() => history.push('/data/Lucy')}>
        Lucy
      </Button>
      <Button colorScheme="red" onClick={() => history.push('/data/Mike')}>
        Mike
      </Button>
    </Stack>
  );
};

export default Header;
